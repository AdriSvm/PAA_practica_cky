import nltk
from nltk import PCFG
from cfg_cnf_converter import ChomskyConverter, ProbabilisticChomskyConverter
import os

class CKY():

    def __init__(self):
        """
        Initialisation of the class, just put some variables to it's initial state
        """
        self._grammar = None
        self._phrase = []
        self._n = 0
        self._table = None

        self._pgrammar = None
        self._probabilities = []

        self._traza = None

    def _initialise_grammar(self,grammar:str) -> None:
        """
        :param grammar: string with a CFG(Context Free Grammar), may be or not in CNF(Chomsky Normal Form)
        :return: None, saves the grammar in class variables
        """
        G = ChomskyConverter(nltk.CFG.fromstring(grammar))
        G.convert_cfg()
        self._grammar = G.grammar


    def _initialise_phrase(self,phrase) -> None:
        """
        :param phrase: A sentence in string format or a list of words
        :return: None, saves to class variables
        """
        if type(phrase) is list:
            self._phrase = phrase
        elif type(phrase) is str:
            self._phrase = phrase.split()
        else:
            raise Exception("Phrase in incorrect format")

    def _initialise_diagonal_table(self) -> bool:
        """
        Initialises the first values of the dynamic table. These are the nonterminal symbols(lhs)
        associated to terminal ones(rhs)
        :return: A bool indicating that the initialisation has been successful
        """
        for i, word in enumerate(self._phrase):
            if len(self._grammar.productions(rhs=word)) == 0:
                return False
            self._table[i][i] = set(rule.lhs() for rule in self._grammar.productions(rhs=word))

        return True

    def _initialise_table(self) -> bool:
        """
        Initialises the table of dimensions len(self._phrase)*len(self._phrase)
        with empty sets and calls the initialisation of the main diagonal
        :return: A bool indication that the creation has been successful
        """
        if self._grammar and len(self._phrase) > 0:
            self._n = len(self._phrase)
            self._table = [[set() for _ in range(self._n)] for _ in range(self._n)]
            if not self._initialise_diagonal_table():
                return False
            return True
        else:
            self._n = 0
            self._table = [[]]
            return False



    def _bottom_up_cky(self) -> None:
        """
        Main method to call for executing the bottom_up CKY algorithm with Dynamic Programming
        :return: None, saves the result to the self._table object
        """
        traza = {}
        if self._grammar and self._table and self._n > 0:
            for j in range(0, self._n):
                for i in range(j - 1, -1, -1):
                    for k in range(i, j):
                        left_cell = self._table[i][k]
                        right_cell = self._table[k + 1][j]
                        for left in left_cell:
                            for right in right_cell:
                                for z in self._grammar.productions(rhs=left):
                                    if len(z.rhs()) > 1 and z.rhs()[1] == right:
                                        self._table[i][j].add(z.lhs())
                                        traza[(i,j)] = (((i,k),(k+1,j)),z.lhs())
                                        if i == k:
                                            traza[(i,k)] = left
                                        if k+1 == j:
                                            traza[(k+1,j)] = right

        self._traza = traza



    def cky_parse(self,words:list, grammar:str) -> bool:
        """
        Initialises the parser which tells whether a sentence complies with a grammar through the
        deterministic CKY algorithm

        :param words (list): List of words in the sentence.
        :param grammar (nltk.CFG): Grammar in normal Chomsky format.

        :return: bool: True if the sentence complies with the grammar, False otherwise.
        """
        self._initialise_grammar(grammar=grammar)
        self._initialise_phrase(phrase=words)
        if not self._initialise_table():
            return False
        self._bottom_up_cky()
        res =  nltk.grammar.Nonterminal('S') in self._table[0][self._n - 1]
        if res:
            self.reconstruir_traza()
        return res

    def reconstruir_traza(self):
        if self._traza is None:
            return ()
        self._i = 0
        def construir_arbre(ar,ele):
            ar.append(ele[1])
            pos_1 = ele[0][0]
            pos_2 = ele[0][1]
            if pos_1[0] == pos_1[1]:
                ar.append([self._traza[pos_1],self._phrase[self._i]])
                self._i += 1
            else:
                ar.append([])
                construir_arbre(ar[len(ar)-1],self._traza[pos_1])
            if pos_2[0] == pos_2[1]:
                ar.append([self._traza[pos_2],self._phrase[self._i]])
                self._i += 1
            else:
                ar.append([])
                construir_arbre(ar[len(ar) - 1], self._traza[pos_2])

        arbre = []
        construir_arbre(arbre,self._traza[(0,len(self._phrase)-1)])
        tr = str(arbre)
        tr = tr.replace(',', "")
        tr = tr.replace('[', "(")
        tr = tr.replace(']', ")")
        self.show_arbre(tr)

    def show_arbre(self,tree:str):
        tree = nltk.Tree.fromstring(tree)
        tree.draw()

    def _initialise_probabilistic_grammar(self, grammar: str) -> None:
        """
        :param grammar: string with a PCFG(Probabilistic Context Free Grammar), must be in CNF(Chomsky Normal Form)
        :return: None, saves the grammar in class variables
        """
        G = ProbabilisticChomskyConverter(PCFG.fromstring(grammar))
        G.convert_pcfg()
        self._pgrammar = G.grammar

    def _initialise_probabilistic_diagonal_table(self) -> bool:
        """
        Initialises the first values of the dynamic table. These are the nonterminal symbols(lhs)
        associated to terminal ones(rhs) along with their probabilities.
        :return: A bool indicating that the initialisation has been successful
        """
        for i, word in enumerate(self._phrase):
            if len(self._pgrammar.productions(rhs=word)) == 0:
                return False
            for rule in self._pgrammar.productions(rhs=word):
                self._probabilities[i][i][rule.lhs()] = rule.prob()
        return True

    def initialise_ptable(self) -> bool:
        """
        Initialises the table of dimensions len(self._phrase)*len(self._phrase)
        with empty dictionaries and calls the initialisation of the main diagonal
        :return: A bool indication that the creation has been successful
        """
        if self._pgrammar and len(self._phrase) > 0:
            self._n = len(self._phrase)
            self._probabilities = [[{} for _ in range(self._n)] for _ in range(self._n)]
            if not self._initialise_probabilistic_diagonal_table():
                return False
            return True
        else:
            self._n = 0
            self._probabilities = [[]]
            return False

    def _bottom_up_pcky(self) -> None:
        """
        Main method to call for executing the bottom_up Probabilistic CKY algorithm with Dynamic Programming
        :return: None, saves the result to the self._probabilities object
        """
        traza = {}
        if self._pgrammar and self._probabilities and self._n > 0:
            for j in range(1, self._n):
                for i in range(j - 1, -1, -1):
                    for k in range(i, j):
                        for rule in self._pgrammar.productions():
                            if len(rule.rhs()) == 2:
                                B, C = rule.rhs()
                                if B in self._probabilities[i][k] and C in self._probabilities[k + 1][j]:
                                    prob = self._probabilities[i][k][B] * self._probabilities[k + 1][j][
                                        C] * rule.prob()
                                    if rule.lhs() not in self._probabilities[i][j] or prob > \
                                            self._probabilities[i][j][rule.lhs()]:
                                        self._probabilities[i][j][rule.lhs()] = prob
                                        traza[(i,j)] = (((i,k),(k+1,j)),rule.lhs())
                                        if i == k:
                                            traza[(i,k)] = B
                                        if k+1 == j:
                                            traza[(k+1,j)] = C

        self._traza = traza

    def pcky_parse(self, words: list, grammar: str) -> float:
        """
        Initialises the parser which tells whether a sentence complies with a grammar through the
        probabilistic CKY algorithm

        :param words (list): List of words in the sentence.
        :param grammar (str): Probabilistic Grammar in normal Chomsky format.

        :return: float: The probability of the sentence given the grammar. Zero if the sentence does not comply with the grammar.
        """
        self._initialise_probabilistic_grammar(grammar=grammar)
        self._initialise_phrase(phrase=words)
        if not self.initialise_ptable():
            return 0.0
        self._bottom_up_pcky()
        res = self._probabilities[0][self._n - 1].get(nltk.grammar.Nonterminal('S'), 0.0)
        if res:
            self.reconstruir_traza()
        return res


