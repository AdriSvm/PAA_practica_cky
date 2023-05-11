import nltk
from nltk import PCFG
from cfg_cnf_converter import ChomskyConverter

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
        self.grammar = G.convert_cfg()

    def _initialise_probabilistic_grammar(self,grammar:str):
        self._pgrammar = PCFG.fromstring(grammar)

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

    def initialise_ptable(self) -> None:
        self._probabilities = [[{} for _ in range(self._n)] for _ in range(self._n)]


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
                                    print(z.rhs())
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

    def _parse_with_probabilities(self):
            for j in range(0, self._n):
                for i in range(j - 1, -1, -1):
                    for k in range(i, j):
                        left_cell = self._table[i][k]
                        right_cell = self._table[k + 1][j]
                        for left in left_cell:
                            for right in right_cell:
                                for z in self._pgrammar.productions(rhs=left):
                                    if z.rhs()[1] == right:
                                        prob = z.prob()
                                        if z.lhs() not in self._probabilities[i][j]:
                                            self._probabilities[i][j][z.lhs()] = prob
                                        else:
                                            self._probabilities[i][j][z.lhs()] = max(self._probabilities[i][j][z.lhs()], prob)

            return self._probabilities[0][self._n - 1]
    def ckyp_parse(self,words,grammar):
        """
        Initialises the parser which tells whether a sentence complies with a grammar through the
        probabilistic CKY algorithm

        :param words (list): List of words in the sentence.
        :param grammar (nltk.CFG): Grammar in normal Chomsky format.

        :return: bool: True if the sentence complies with the grammar, False otherwise.
        """
        self._initialise_probabilistic_grammar(grammar=grammar)
        self._initialise_phrase(phrase=words)
        self._i
        self._parse_with_probabilities()
        # The sentence complies with the grammar if S is in cell (0, self._n-1)
        return nltk.grammar.Nonterminal('S') in self._table[0][self._n - 1]


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
                A -> 'a' D
                B -> 'b'
                C -> 'c'
                D -> 'g'
                """
        sentences = [
            "abc",
            "aabb"
        ]
        for sentence in sentences:
            if self.cky_parse(list(sentence), grammar):
                print(f"'{sentence}' cumple con la gramática")
            else:
                print(f"'{sentence}' no cumple con la gramática")


a = CKY()
a.joc_de_proves2()