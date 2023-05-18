
from models import *
import re

alg = CKY()

with open("PAA_practica_cky\proves.txt", encoding="utf-8") as p:
    doc = p.readlines()
    long = len(doc)
    n = 0
    while n < long:
        if len(doc[n].split()) > 0 and doc[n].split()[0] == "Exemple":
            print(doc[n], end="")
            n += 1
            if len(doc[n]) > 0 and doc[n].split()[0] == "Gramática":
                tipus = "det" if len(doc[n].split()) == 1 else "prob"
                n += 1

            gram = """"""
            while len(doc[n].split()) != 0:
                gram += str(doc[n])
                n += 1

            n += 1
            phrases = doc[n].split(",")
            for phrase in phrases:
                phrase = phrase.replace("\n", "")
                if len(phrase.split(" ")) == 1:
                    phrase = list(phrase)
                if tipus == "det":
                    print("Input: ", phrase)
                    print("Resultat:", alg.cky_parse(phrase, gram))
                    print()
                else:
                    r = alg.pcky_parse(phrase, gram)
                    print("Input: ", phrase)
                    print("Resultat:", True if r else False, ", probabilitat:", r)
                    print()
        
        n += 1

        