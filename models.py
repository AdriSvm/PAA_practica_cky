import nltk

class CKY():

    def __init__(self):
        self._grammar = None
        self._phrase = []
        self._n = 0
        self._table = None

    def _initialise_grammar(self,grammar:str) -> None:
        self._grammar = nltk.CFG.fromstring(grammar)
        if not self._grammar_is_cnf():
            cnf_gram = self._chomsky_normal_form()
            if cnf_gram:
                self._grammar = cnf_gram
            else:
                raise Exception('Grammar could not be converted to CNF form')
            
    def _initialise_phrase(self,phrase) -> None:
        if type(phrase) is list:
            self._phrase = phrase
        elif type(phrase) is str:
            self._phrase = phrase.split()
        else:
            raise Exception("Phrase in incorrect format")

    def _initialise_diagonal_table(self):
        for i, word in enumerate(self._phrase):
            self._table[i][i] = set(rule.lhs() for rule in self._grammar.productions(rhs=word))

    def _initialise_table(self) -> None:
        if self._grammar and len(self._phrase) > 0:
            self._n = len(self._phrase)
            self._table = [[set() for _ in range(self._n)] for _ in range(self._n)]
            self._initialise_diagonal_table()
        else:
            self._n = 0
            self._table = [[]]


    def _grammar_is_cnf(self) -> bool:
        if self._grammar:
            return self._grammar.is_chomsky_normal_form()
        return False

    def _chomsky_normal_form(self) -> bool:
        if self._grammar:
            return self._grammar.chomsky_normal_form()
        return False

    def _bottom_up_cky(self):
        # Llenar la tabla CKY de manera recursiva
        if self._grammar and self._table and self._n > 0:
            for j in range(0, self._n):
                for i in range(j - 1, -1, -1):
                    for k in range(i, j + 1):
                        print(self._table)
                        left_cell = self._table[i][k]
                        right_cell = self._table[k + 1][j]
                        for i in self._grammar.productions(rhs=(left_cell, right_cell)):
                            self._table[i, j].add(i.lhs())

    def cky_parse(self,words:list, grammar:str) -> bool:
        """
        Implementación del algoritmo CKY para determinar si una oración cumple con una gramática.

        Parameters:
        words (list): Lista de palabras de la oración.
        grammar (nltk.CFG): Gramática en formato Chomsky normal.

        Returns:
        bool: True si la oración cumple con la gramática, False en caso contrario.
        """
        self._initialise_grammar(grammar=grammar)
        self._initialise_phrase(phrase=words)
        self._initialise_table()

        # La oración cumple con la gramática si S está en la celda (0, self._n-1)
        return nltk.grammar.Nonterminal('S') in self._table[0][self._n - 1]