import nltk
from nltk import PCFG
from cfg_cnf_converter import ChomskyConverter, ProbabilisticChomskyConverter

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
        # Llenar la tabla CKY de manera recursiva
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
        # The sentence complies with the grammar if S is in cell (0, self._n-1)
        return nltk.grammar.Nonterminal('S') in self._table[0][self._n - 1]


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
            self._probabilities = [[{} for _ in range(self._n)] for _ in range(self._n)]
            return False

    def _bottom_up_pcky(self) -> None:
        """
        Main method to call for executing the bottom_up Probabilistic CKY algorithm with Dynamic Programming
        :return: None, saves the result to the self._probabilities object
        """
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
        # The sentence complies with the grammar if S is in cell (0, self._n-1)
        return self._probabilities[0][self._n - 1].get(nltk.grammar.Nonterminal('S'), 0.0)

    def joc_de_proves(self):
        grammar = """
            S -> NP VP
            NP -> Det N
            VP -> V NP
            Det -> 'the' | 'a'
            N -> 'cat' | 'dog' | 'table' | 'house'
            V -> 'chases' | 'sleeps' | 'sits'
        """
        sentences = [
            "the cat chases a dog",
            "a dog sleeps on the table",
            "the house sits on the table",
            "a cat chases the dog",
            "the dog sleeps on a house"
        ]
        for sentence in sentences:
            if self.cky_parse(sentence.split(), grammar):
                print(f"'{sentence}' cumple con la gramática")
            else:
                print(f"'{sentence}' no cumple con la gramática")


    def joc_de_proves2(self):
        grammar = """
                    S -> 'a' | X A | A X | 'b'
                    A -> R B
                    B -> A X | 'b' | 'a'
                    X -> 'a'
                    R -> X B
                """
        grammar = """
                S -> A B | A C
                A -> 'a'
                B -> 'b'
                C -> 'c'
                D -> 'g'
                """
        sentences = [
            "ab",
            "ac",
            "aac"
        ]
        for sentence in sentences:
            if self.cky_parse(list(sentence), grammar):
                print(f"'{sentence}' cumple con la gramática")
            else:
                print(f"'{sentence}' no cumple con la gramática")

    def joc_de_proves_pcfg1(self):
        grammar_cnf = """
            S -> A B [1.0]
            A -> 'a' [1.0]
            B -> C D [1.0]
            C -> 'b' [1.0]
            D -> E F [1.0]
            E -> 'c' [1.0]
            F -> 'd' [1.0]
        """

        sentences = ["abcd"]

        for sentence in sentences:
            if self.pcky_parse(list(sentence),grammar_cnf):
                print(f"'{sentence}' cumple con la gramática")
            else:
                print(f"'{sentence}' no cumple con la gramática")

    def joc_de_proves_pcfg2(self):
        grammar_cnf = """
            S -> A B C D [1.0]
            A -> 'a' [1.0]
            B -> 'b' [1.0]
            C -> 'c' [1.0]
            D -> 'd' [1.0]
        """

        sentences = ["abc"]

        for sentence in sentences:
            res = self.pcky_parse(list(sentence),grammar_cnf)
            if res:
                print(f"'{sentence}' cumple con la gramática con probabilidad",res)
            else:
                print(f"'{sentence}' no cumple con la gramática, prob:", res)



a = CKY()
a.joc_de_proves_pcfg2()