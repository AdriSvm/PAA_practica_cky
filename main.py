def cky(grammar, word):
    """
    Determina si una palabra pertenece al lenguaje inducido por una gramática
    en forma normal de Chomsky, usando el algoritmo CKY.

    :param grammar: una gramática en forma normal de Chomsky representada como
                    un diccionario donde las claves son símbolos no terminales
                    y los valores son listas de producciones
    :param word: una palabra representada como una lista de símbolos terminales
    :return: True si la palabra pertenece al lenguaje inducido por la gramática,
             False en caso contrario
    """
    n = len(word)
    table = [[set() for j in range(n + 1)] for i in range(n)]

    # Inicialización de la diagonal
    for i in range(n):
        for nt, prod in grammar.items():
            for p in prod:
                if len(p) == 1 and p[0] == word[i]:
                    table[i][i + 1].add(nt)

    # Completar la tabla
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l
            for k in range(i + 1, j):
                for nt, prod in grammar.items():
                    for p in prod:
                        if len(p) == 2 and p[0] in table[i][k] and p[1] in table[k][j]:
                            table[i][j].add(nt)

    # Comprobar si la palabra pertenece al lenguaje
    return 'S' in table[0][n]


grammar = {
    'S': [['NP', 'VP']],
    'NP': [['Det', 'N'], ['NP', 'PP']],
    'PP': [['P', 'NP']],
    'VP': [['V', 'NP'], ['VP', 'PP']],
    'Det': [['the'], ['a']],
    'N': [['cat'], ['dog'],['couch']],
    'P': [['on'], ['in']],
    'V': [['sleeps'], ['chases']]
}


word1 = ['the', 'cat','sleeps', 'on','the','couch']
word2 = ['the', 'dog', 'chases', 'a', 'cat']
word3 = ['the', 'cat', 'in', 'the', 'hat']

'''print(cky(grammar, word1)) # True
print(cky(grammar, word2)) # True
print(cky(grammar, word3)) # False'''

import nltk


def cky_parse(words, grammar):
    """
    Implementación del algoritmo CKY para determinar si una oración cumple con una gramática.

    Parameters:
    words (list): Lista de palabras de la oración.
    grammar (nltk.CFG): Gramática en formato Chomsky normal.

    Returns:
    bool: True si la oración cumple con la gramática, False en caso contrario.
    """
    n = len(words)

    # Inicializar la tabla CKY
    table = [[set() for _ in range(n)] for _ in range(n)]

    # Llenar la diagonal de la tabla CKY con las producciones correspondientes a las palabras de la oración
    for i, word in enumerate(words):
        table[i][i] = set(rule.lhs() for rule in grammar.productions(rhs=word))

    # Llenar la tabla CKY de manera recursiva
    for j in range(0, n):
        for i in range(j-1, -1, -1):
            for k in range(i, j+1):
                print(table)
                left_cell = table[i][k]
                right_cell = table[k+1][j]
                for i in grammar.productions(rhs=(left_cell,right_cell)):
                    table[i,j].add(i.lhs())


    # La oración cumple con la gramática si S está en la celda (0, n-1)
    return nltk.grammar.Nonterminal('S') in table[0][n-1]


# Definición de la gramática
grammar = nltk.CFG.fromstring("""
    S -> NP VP
    NP -> Det N
    VP -> V NP
    Det -> 'the' | 'a'
    N -> 'cat' | 'dog' | 'table' | 'house'
    V -> 'chases' | 'sleeps' | 'sits'
""")

print(grammar.is_chomsky_normal_form())
# Ejemplo de frases que cumplen la gramática
sentences = [
    "the cat chases a dog",
    "a dog sleeps on the table",
    "the house sits on the table",
    "a cat chases the dog",
    "the dog sleeps on a house"
]


for sentence in sentences:
    if cky_parse(sentence.split(), grammar):

        print(f"'{sentence}' cumple con la gramática")
        break
    else:

        print(f"'{sentence}' no cumple con la gramática")
        break

# Salida:
# 'the cat chases a dog' cumple con la gramática
# 'a dog sleeps on the table' cumple con la gramática
# 'the house sits on the table' no cumple con la gramática
# 'a cat chases the dog' no cumple con la gramática
# 'the dog sleeps on a house' no cumple con la gramática

