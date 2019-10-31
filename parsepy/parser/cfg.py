from __future__ import annotations
from typing import Any, List, Union, Hashable, Set, Iterator

from parsepy.parser import error
from parsepy.lexer.lexer import Lexer


class CFG:
    """

    """

    EPSILON = None

    class NonTerm:
        """

        """

        def __init__(self, name: str):
            """

            :param name:
            """

            self.name: str = name

        def __str__(self) -> str:
            """

            :return:
            """

            return self.name

        def __repr__(self) -> str:
            """

            :return:
            """

            return "Non-Term({})".format(self.name)

        def __eq__(self, other: Any) -> bool:
            """

            :param other:
            :return:
            """

            if isinstance(other, CFG.NonTerm):
                return self.name == other.name
            else:
                return False

        def __ne__(self, other: Any) -> bool:
            if isinstance(other, CFG.NonTerm):
                return self.name != other.name
            else:
                return True

        def __hash__(self):
            return hash(self.name)

    class Prod:
        """

        """

        def __init__(self, rule: CFG.NonTerm, prod: List[Union[str, CFG.NonTerm, CFG.EPSILON.__class__]], idx: int = 0):
            """

            :param rule:
            :param prod:
            """

            self.rule: CFG.NonTerm = rule
            self.prod: List[str, CFG.NonTerm, CFG.EPSILON.__class__] = prod
            self.idx: int = idx

        def __str__(self) -> str:
            """

            :return:
            """

            return "{} -> {}".format(self.rule.name, self.items_str())

        def items_str(self) -> str:
            """

            :return:
            """

            return ' '.join(i.name if isinstance(i, CFG.NonTerm) else i for i in self.prod) if self else '\u03B5'

        def __bool__(self) -> bool:
            """

            :return:
            """

            return CFG.EPSILON not in self.prod

        def __len__(self) -> int:
            """

            :return:
            """

            return 0 if CFG.EPSILON in self.prod else len(self.prod)

        def __getitem__(self, idx):
            """

            :param idx:
            :return:
            """

            return self.prod[idx]

        def __iter__(self):
            """

            :return:
            """

            return iter(self.prod)

    def __init__(self, prods: List[CFG.Prod], start: Hashable = 'Start'):
        """

        :param prod:
        :param start:
        """

        # Check prods for dangling Non-Terms
        self.productions = prods
        for n, prod in enumerate(self.productions):
            prod.idx = n
        for prod in self.productions:
            for i in prod:
                if isinstance(i, CFG.NonTerm) and i not in self.rules:
                    raise error.CFGError("Undefined Non-Terminal: {}".format(i))

        if start not in [r.name for r in self.rules]:
            raise error.CFGError("Invalid Start Rule: {}".format(start))
        self.start = start

    @property
    def rules(self) -> List[CFG.NonTerm]:
        """

        :return:
        """

        return set(p.rule for p in self.productions)

    def __contains__(self, item):
        """

        :param item:
        :return:
        """

        if isinstance(item, CFG.NonTerm):
            return item in self.rules
        elif isinstance(item, CFG.Prod):
            return item in self.productions
        raise TypeError("unsupported operand type(s) for in: '{}' and '{}'".format(item.__class__, self.__class__))

    def first(self, rule: Union[CFG.NonTerm, str, CFG.EPSILON.__class__, List[Union[CFG.NonTerm, str, CFG.EPSILON.__class__]]]) -> Set[Union[Hashable, CFG.EPSILON.__class__]]:
        """

        :param rule:
        :return:
        """

        if isinstance(rule, list):
            f = set()
            for r in rule:
                f |= self.first(r)
                if CFG.EPSILON in f:
                    f -= {CFG.EPSILON}
                else:
                    return f
            return f | {CFG.EPSILON}



        # { X in terminals }
        if isinstance(rule, str) or rule == CFG.EPSILON:
            if rule in (r.name for r in self.rules):
                rule = CFG.NonTerm(rule)
            else:
                return {rule}
        elif not isinstance(rule, CFG.NonTerm):
            raise TypeError("unsupported type: {} for FIRST".format(rule.__class__))

        if rule not in self:
            raise error.CFGError("Non-Term({}) is not a rule".format(rule))

        out = set()

        for prod in self.productions:
            if prod.rule == rule:
                pout = set()

                # epsilon if X -> epsilon exists
                if not prod:
                    out |= {CFG.EPSILON}
                    continue
                ep = True
                for item in prod:

                    # FIRST(item)
                    f = self.first(item)
                    pout |= f

                    # FIRST(Yi) for X -> Y1 Y2 .. Yk if for all j < i < k epsilon is in FIRST(Yj)
                    if CFG.EPSILON not in f:
                        ep = False
                        break

                # All items can go to epsilon
                if ep:
                    out |= {CFG.EPSILON}

                # May be unnecessary, possible 'Lacks Pairwise Disjointness Detection
                out |= pout
        return out

    def follow(self, rule: CFG.NonTerm) -> Set[Union[Hashable, Lexer.EOI.__class__]]:
        """

        :param rule:
        :return:
        """

        if not isinstance(rule, CFG.NonTerm):
            if rule in (r.name for r in self.rules):
                rule = CFG.NonTerm(rule)
            else:
                raise TypeError("unsupported type: {} for FIRST".format(rule.__class__))

        if rule not in self:
            raise error.CFGError("Non-Term({}) is not a rule".format(rule))

        out = set()

        # $ in FOLLOW(X) if X is start rule
        if self.start == rule.name:
            out |= {Lexer.EOI}

        # Find rule in productions
        for prod in self.productions:
            for i in range(len(prod)):
                if prod[i] == rule:

                    # X -> aB, FOLLOW(X) is in FOLLOW(B)
                    if i + 1 == len(prod):
                        if rule != prod.rule:
                            out |= self.follow(prod.rule)

                    # X -. aBb
                    else:
                        f = self.first(prod[i+1:])
                        if CFG.EPSILON in f:
                            if rule != prod.rule:
                                out |= self.follow(prod.rule)
                        out |= f - {CFG.EPSILON}
        return out

    def select(self, prod: CFG.Prod) -> Set[Hashable, Lexer.EOI.__class__]:
        """

        :param prod:
        :return:
        """

        out = self.first(prod.prod)
        if CFG.EPSILON in out:
            out = (out - {CFG.EPSILON}) | self.follow(prod.rule)
        return out

    def parse(cfgstr: Union[str, Iterator[str]]) -> CFG:
        """

        :return:
        """

        if isinstance(cfgstr, str):
            rules = cfgstr.splitlines()
        else:
            rules = cfgstr
        start = None
        prods = []
        for rule in rules:
            rl, i = rule.split('->')
            rl = rl.strip()
            if start is None:
                start = rl
            for p in i.split('|'):
                p = [a for a in p.split()]
                if not p or '\u03B5' in p:
                    prods += [(CFG.NonTerm(rl), [CFG.EPSILON])]
                else:
                    prods += [(CFG.NonTerm(rl), p)]
        rls = set(prod[0].name for prod in prods)
        for n, p in enumerate(prods):
            items = [(CFG.NonTerm(item) if (item in rls) else item) for item in p[1]]
            prods[n] = (p[0], items)
        return CFG([CFG.Prod(p[0], p[1]) for p in prods], start)

    @property
    def terms(self):
        """

        :return:
        """

        out = set()
        for prod in self.productions:
            if prod:
                out |= set(prod.prod)
        return out - self.rules

    def printCFG(self):
        print("Start: {}".format(self.start))
        for rule in self.rules:
            rule_str = "{} -> ".format(rule)
            n = 0
            for production in self.productions:
                if production.rule == rule:
                    if n > 0:
                        rule_str += " | "
                    rule_str += production.items_str()
                    n += 1
            print(rule_str)