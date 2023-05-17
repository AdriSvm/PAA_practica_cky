import nltk
from nltk import CFG, PCFG, Nonterminal, Production, ProbabilisticProduction


class ChomskyConverter:
    def __init__(self, grammar:CFG) -> None:
        self.grammar = grammar
        self.non_terminal_count = 0


    def convert_cfg(self) -> nltk.grammar:
        """
        :return: CFG gramatic converted to CNF
        """
        if not self.is_chomsky_normal_form():
            self.remove_unitaries()
            self.remove_unreachable()
            self.remove_3mprods()
            self.change_terminals()
        return self.grammar

    def is_chomsky_normal_form(self) -> bool:
        """
        :return: bool whether the self.grammar is or not in chomsky normal form (CNF)
        """
        return all([not self.are_unitary_rules(),not self.are_3mprods(),
                        not self.are_malformed_terminals()])
    def is_unitary_nt(self,prod:Production) -> bool:
        """
        :param prod: object of nltk.Production
        :return: Whether the production is unitary and, it's rhs is Nonterminal
        """
        return len(prod.rhs()) == 1 and isinstance(prod.rhs()[0],Nonterminal)

    def is_unitary(self,prod:Production) -> bool:
        """
        :param prod: object of nltk.Production
        :return: Whether the production is or not unitary. Doesn't affect if it's Nonterminal or Terminal
        """
        return len(prod.rhs()) == 1

    def are_unitary_rules(self):
        """
        :return: Whether there are or not Unitary rules of Nonterminals in self.grammar
        """
        for prod in self.grammar.productions():
            if len(prod.rhs()) == 1 and isinstance(prod.rhs()[0],Nonterminal):
                return True
        return False

    def rhss(self,prods:Production) -> list:
        """
        :param prods: List of Production objects from nltk
        :return: All rhs() of all the productions in a list
        """
        rhss = []
        for p in prods:
            for i in p.rhs():
                rhss.append(i)
        return rhss

    def remove_unitaries(self) -> None:
        """
        Removes all the unitary Nonterminal productions in the self.grammar object
        :return: None
        """
        while self.are_unitary_rules():
            prods = []
            for prod in self.grammar.productions():
                if self.is_unitary_nt(prod):
                    for pr in self.grammar.productions(lhs=prod.rhs()[0]):
                        prods.append(Production(prod.lhs(),pr.rhs()))

                elif prod not in prods:
                    prods.append(prod)

            if prods:
                self.grammar = CFG(self.grammar.start(), prods)

    def grammar_BFS(self) -> set:
        """
        :return: All the productions in a BFS order of the self.grammar object
        """
        reachable = set()
        reachable.add(self.grammar.start())

        queue = [self.grammar.start()]
        while queue:
            symbol = queue.pop(0)
            productions = self.grammar.productions(lhs=symbol)
            for production in productions:
                for rhs in production.rhs():
                    if not rhs in reachable:
                        reachable.add(rhs)
                        queue.append(rhs)
        return reachable
    def remove_unreachable(self) -> None:
        """
        Removes all unreachable productions of the self.grammar object
        :return: None
        """
        reachable_symbols = self.grammar_BFS()

        new_productions = [p for p in self.grammar.productions() if p.lhs() in reachable_symbols and all(
            s in reachable_symbols or isinstance(s, str) for s in p.rhs())]

        if new_productions:
            self.grammar = CFG(self.grammar.start(),new_productions)

    def are_3mprods(self) -> bool:
        """
        :return: Whether there are 3 or more symbols in the right hand of any production of self.grammar object
        """
        for prod in self.grammar.productions():
            if len(prod.rhs()) > 2:
                return True
        return False
    def remove_3mprods(self) -> None:
        """
        Processes all productions with more than 3 symbols in its right hand of the object self.grammar
        :return: None
        """
        counter_nt = 0

        while self.are_3mprods():
            new_prods = []
            for prod in self.grammar.productions():
                if len(prod.rhs()) > 2:
                    new_nt = Nonterminal(f"X{counter_nt}")
                    counter_nt += 1
                    new_prods.append(Production(lhs=prod.lhs(),rhs=[prod.rhs()[0],new_nt]))
                    new_prods.append(Production(lhs=new_nt,rhs=[i for i in prod.rhs()[1:]]))

                else:
                    new_prods.append(prod)

            if new_prods:
                self.grammar = CFG(start=self.grammar.start(),productions=new_prods)

    def are_more_terminals(self,production:Production):
        """
        :param production: A Production object of nltk
        :return: bool whether the production or the self.grammar have mo
        """
        if production:
            return not all([isinstance(i,Nonterminal) for i in production.rhs()])


    def are_malformed_terminals(self):
        for prod in self.grammar.productions():
            if len(prod.rhs()) > 1 and not all([isinstance(i,Nonterminal) for i in prod.rhs()]):
                return True
        return False
    def change_terminals(self):
        counter_nt = 0
        new_prods = []
        for pr in self.grammar.productions():
            if not self.is_unitary(pr) and self.are_more_terminals(production=pr):
                rhss = []
                for symbol in pr.rhs():
                    if isinstance(symbol,str):
                        new_nt = Nonterminal(f"Y{counter_nt}")
                        counter_nt += 1

                        new_prods.append(Production(lhs=new_nt,rhs=[symbol]))
                        rhss.append(new_nt)
                    else:
                        rhss.append(symbol)
                new_prods.append(Production(lhs=pr.lhs(),rhs=rhss))

            elif pr not in new_prods:
                new_prods.append(pr)

        if new_prods:
            self.grammar = nltk.CFG(start=self.grammar.start(),productions=new_prods)


class ProbabilisticChomskyConverter(ChomskyConverter):
    def __init__(self, grammar: PCFG) -> None:
        super().__init__(grammar)
        self.non_terminal_count = 0

    def convert_pcfg(self) -> nltk.grammar:
        """
        :return: PCFG gramatic converted to CNF
        """
        if not self.is_chomsky_normal_form():
            self.remove_unitaries()
            self.remove_unreachable()
            self.remove_3mprods()
            self.change_terminals()
        return self.grammar
    
    def remove_unitaries(self) -> None:
        """
        Removes all the unitary Nonterminal productions in the self.grammar object
        :return: None
        """
        while self.are_unitary_rules():
            prods = []
            for prod in self.grammar.productions():
                if self.is_unitary_nt(prod):
                    for pr in self.grammar.productions(lhs=prod.rhs()[0]):
                        prods.append(ProbabilisticProduction(prod.lhs(),pr.rhs(), prob=prod.prob()*pr.prob()))

                elif prod not in prods:
                    prods.append(prod)

            if prods:
                self.grammar = PCFG(self.grammar.start(), prods)



    def remove_3mprods(self) -> None:
        """
        Processes all productions with 3 or more symbols in its right hand of the object self.grammar
        :return: None
        """
        counter_nt = 0
        while self.are_3mprods():
            new_prods = []
            for prod in self.grammar.productions():
                if len(prod.rhs()) > 2:
                    new_nt = Nonterminal(f"X{counter_nt}")
                    counter_nt += 1
                    new_prods.append(ProbabilisticProduction(lhs=prod.lhs(),rhs=[prod.rhs()[0],new_nt], prob=prod.prob()))
                    new_prods.append(ProbabilisticProduction(lhs=new_nt,rhs=[i for i in prod.rhs()[1:]], prob=1.0))

                else:
                    new_prods.append(prod)

            if new_prods:
                self.grammar = PCFG(start=self.grammar.start(),productions=new_prods)

    def change_terminals(self):
        counter_nt = 0
        new_prods = []
        for pr in self.grammar.productions():
            if not self.is_unitary(pr) and self.are_more_terminals(production=pr):
                rhss = []
                for symbol in pr.rhs():
                    if isinstance(symbol,str):
                        new_nt = Nonterminal(f"Y{counter_nt}")
                        counter_nt += 1

                        new_prods.append(ProbabilisticProduction(lhs=new_nt,rhs=[symbol], prob=1.0))
                        rhss.append(new_nt)
                    else:
                        rhss.append(symbol)
                new_prods.append(ProbabilisticProduction(lhs=pr.lhs(),rhs=rhss, prob=pr.prob()))

            elif pr not in new_prods:
                new_prods.append(pr)

        if new_prods:
            self.grammar = PCFG(start=self.grammar.start(),productions=new_prods)