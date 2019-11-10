from typing import Dict, Callable, Iterable, Optional, Hashable, Any, Iterator

from os import PathLike

from parsepy.lexer import Lexer
from parsepy.parser import AST
from parsepy.parser import error
from parsepy.parser import CFG, Parser


class LL1(Parser):
    """

    """

    def __init__(self, lexer: Lexer, cfg: CFG, actions: Dict[int, Callable] = {}):
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
                    raise error.ParserError("Ambiguous Grammar in rule {}".format(prod.rule))

    def eval_file(self, path: PathLike) -> Any:
        """


        :param path:
        :return:
        """

        return self.tree_from_file(path).eval()

    def tree_from_file(self, path: PathLike, start: Optional[Hashable] = None) -> AST:
        """

        :param start:
        :param path:
        :return:
        """

        return self.tree(self.get_tokens_from_file(path), start, path)

    def eval(self, string: Iterable) -> Any:
        """

        :param string:
        :return:
        """

        return self.tree(string).eval()

    def tree(self, string: Iterable, start: Optional[Hashable] = None, path: PathLike = "") -> AST:
        """

        :param string:
        :param start:
        :param path:
        :return:
        """

        if not path:
            path = repr(string.__class__)

        if isinstance(string, Iterator):
            t_iter = string
        else:
            t_iter = self.get_tokens(string, path)
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
                curr.add_child(AST(tok, None, tok.line, tok.col, tok.file))
                while pops[-1] == 0:
                    pops.pop()
                    curr = curr.parent
                tok = next(t_iter)
            elif Lexer.EOI != tok.type and tok.type not in self.cfg.terms:
                raise error.UnexpToken(tok, set(self.lltable[ps[-1]].keys()))
            elif Lexer.UNK == tok.type:
                raise error.UnkToken(tok)
            elif tok.type not in self.lltable[ps[-1]]:
                raise error.UnkToken(tok, set(self.lltable[ps[-1]].keys()))
            else:
                prod = self.lltable[ps[-1]][tok.type]
                r = ps.pop()
                pops[-1] -= 1

                pops += [len(prod)]
                try:
                    act = self.actions[prod.idx]
                except KeyError:
                    act = None
                curr.add_child(AST(prod, act, tok.line, tok.col, tok.file))
                curr = curr.children[-1]
                if not prod:
                    curr.add_child(AST(CFG.EPSILON, None))
                    while curr.parent and pops[-1] == 0:
                        pops.pop()
                        curr = curr.parent
                else:
                    ps += reversed(prod.prod)
        return out_tree[0]


def test():
    from collections import namedtuple

    tokreg = {
        "t_plus": r"\+",
        "t_mult": r"\*",
        "t_lparen": r"\(",
        "t_rparen": r"\)",
        "t_id": r"[A-Za-z_]\w*",
        "t_ws": r"[ \t]+",
    }

    act = {"t_ws": lambda a: None}

    lexer = Lexer(tokreg, act)

    cfg_str = """E  -> T E'
                E' -> t_mult T E' | \u03B5
                T  -> F T'
                T' -> t_plus F T' |
                F  -> t_lparen E t_rparen | t_id"""

    cfg = CFG.parse(cfg_str)

    ids = {'A': 1, 'B': 2, 'X': 4, 'C': 0}

    OPLST = namedtuple('OPLST', 'op operand')

    def e(vals):
        if vals[1].op is None:
            return vals[0]
        elif vals[1].op == '*':
            return vals[0] * vals[1].operand

    def ep1(vals):
        return OPLST(op=vals[0], operand=e(vals[1:]))

    def ep2(vals):
        return OPLST(op=None, operand=None)

    def t(vals):
        if vals[1].op is None:
            return vals[0]
        elif vals[1].op == '+':
            return vals[0] + vals[1].operand

    def tp1(vals):
        return OPLST(op=vals[0], operand=t(vals[1:]))

    def tp2(vals):
        return OPLST(op=None, operand=None)

    def f1(vals):
        return vals[1]

    def f2(vals):
        return ids[vals[0]]

    parser = LL1(lexer, cfg, {0: e, 1: ep1, 2: ep2, 3: t, 4: tp1, 5: tp2, 6: f1, 7: f2})

    string = "X*(A*X+B)+C"

    # tree = parser.tree("X*(A*X+B)+C")

    # tree.print_tree()

    print(parser.eval(string))


if __name__ == "__main__":
    test()
