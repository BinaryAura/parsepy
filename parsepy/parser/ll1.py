from typing import Dict, Callable, Iterable, Optional, Hashable

from parsepy.lexer import Lexer
from parsepy.parser.error import ParserError, UnexpToken, UnkToken
from parsepy.parser.parser import CFG, Parser


class LL1(Parser):
    """

    """

    def __init__(self, lexer: Lexer, cfg: CFG, actions: Dict[CFG.NonTerm, Callable]):
        """

        :param lexer:
        :param cfg:
        :param actions:
        """

        super().__init__(lexer, cfg, actions)

        self.lltable = {t: {} for t in cfg.rules}
        for prod in cfg.productions:
            for sym in cfg.select(prod):
                if sym not in self.lltable[prod.rule]:
                    self.lltable[prod.rule][sym] = prod
                else:
                    raise ParserError("Ambiguous Grammar in rule {}".format(prod.rule))

    def eval(self, string: Iterable) -> AST:
        tree = self.tree(string)
        return tree.eval()

    def tree(self, string: Iterable, start: Optional[Hashable] = None) -> AST:
        if isinstance(string, Iterable):
            t_iter = self.lexer.tokenize(string)
        else:
            raise ValueError("string must be Iterable, found {}".format(string.__class__))
        tok = next(t_iter)
        ps = [Lexer.EOI]
        if start is None or isinstance(start, Hashable):
            ps += [CFG.NonTerm(self.cfg.start if start is None else start)]
        else:
            raise ValueError("start must be None or Hashable, found {}".format(start.__class__))
        out_tree = AST('Root')
        pops = [1]
        curr = out_tree
        while ps[-1] != Lexer.EOI:
            if Lexer.EOI != tok.type and ps[-1] == tok.type:
                t = ps.pop()
                pops[-1] -= 1
                curr.add_child(AST(tok))
                while pops[-1] == 0:
                    pops.pop()
                    curr = curr.parent
                tok = next(t_iter)
            elif Lexer.EOI != tok.type and tok.type not in self.cfg.terms:
                raise UnexpToken(tok, set(self.lltable[ps[-1]].keys()))
            elif Lexer.UNK == tok.type:
                raise UnkToken(tok)
            elif tok.type not in self.lltable[ps[-1]]:
                raise UnkToken(tok, set(self.lltable[ps[-1]].keys()))
            else:
                prod = self.lltable[ps[-1]][tok.type]
                r = ps.pop()
                pops[-1] -= 1

                pops += [len(prod)]
                try:
                    act = self.actions[prod.idx]
                except KeyError:
                    act = None
                curr.add_child(AST(prod, act))
                curr = curr.children[-1]
                if not prod:
                    curr.add_child(AST(CFG.EPSILON, None))
                    while curr.parent and pops[-1] == 0:
                        pops.pop()
                        curr = curr.parent
                else:
                    ps += reversed(prod.prod)
        return out_tree[0]
