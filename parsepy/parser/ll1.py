from typing import Dict, Callable, Iterable, Optional, Hashable, Any, Iterator, Union

from os import PathLike

from parsepy.lexer import Lexer
from parsepy.lexer import Token
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

    def parse_file(self, file: Union[str, PathLike], start: Optional[Hashable] = None):
        with open(file, "r") as f:
            text = f.read()
        return self.parse(text, start, file)

    def parse(self, text: str, start: Optional[Hashable] = None, file: Optional[Union[str, PathLike]] = None) -> AST:
        if start is None or isinstance(start, Hashable):
            start = CFG.NonTerm(self.cfg.start if start is None else start)
        else:
            raise ValueError("start must be None or Hashable, found {}".format(start.__class__))
        if file is None:
            file = str(type(text))
        t_iter = self.lexer.tokenize(text)
        ast, _ = self._r_parse(next(t_iter), t_iter, start)
        return ast

    def _r_parse(self, token: Token, token_iter: Lexer.Iter, symbol: Union[str, CFG.NonTerm]):
        """
        :raise UnkToken:
            When token isn't used by the CFG
        :raise UnexpToken:
            When token breaks the CFG at symbol

        :param token: Token
            current token in parse
        :param token_iter: Lexer.Iter
            Token Iterator for the parse
        :param symbol: Union[str, CFG.NonTerm
            current Symbol in LL1 Table parse

        :return: AST
            An abstract syntax tree of symbol with token_iter
        """

        if Lexer.EOI != token.type and symbol == token.type:
            # Found Token
            ast = AST(token, token.text, None, token.line, token.col, token.file)
            # Get next Token
            token = next(token_iter)
        elif Lexer.EOI != token.type not in self.cfg.terms or Lexer.UNK == token.type:
            # Unknown Token
            raise error.UnkToken(token)
        elif symbol in self.cfg.terms:
            # Unexpected Token
            raise error.UnexpToken(token, {symbol, })
        elif token.type not in self.lltable[symbol]:
            # Unexpected Token
            raise error.UnexpToken(token, set(self.lltable[symbol].keys()))
        else:
            prod = self.lltable[symbol][token.type]
            # Found Production
            try:
                act = self.actions[prod.idx]
            except KeyError:
                act = None
            ast = AST(prod, '', act, token.line, token.col, token.file)

            if len(prod):
                # Iterate through items in Production
                for symbol in prod:
                    # Recurse
                    child_ast, token = self._r_parse(token, token_iter, symbol)
                    ast.add_child(child_ast)
                st_tok = ast.children[0]
                en_tok = ast.children[-1]
                st_line = st_tok.line
                st_col = st_tok.col
                en_line = en_tok.line + en_tok.text.count('\n')
                en_col = en_tok.col + len(en_tok.text) if en_tok.text.count('\n') == 0 else len(en_tok.text) - en_tok.text.rindex('\n')
                raw = token_iter.str_in.splitlines()[st_line-1:en_line]
                raw[0] = raw[0][st_col-1:]
                raw[-1] = raw[-1][:en_col-st_col]
                ast.text = ''.join(raw)
            else:
                # Found epsilon production
                pass
        return ast, token

    def eval_file(self, path: PathLike) -> Any:
        """


        :param path:
        :return:
        """

        return self.parse_file(path).eval()

    def eval(self, string: Iterable) -> Any:
        """

        :param string:
        :return:
        """

        return self.parse(string).eval()


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

    def op(op, a, b):
        if op == '+':
            return a + b
        elif op == '-':
            return a-b
        elif op == '*':
            return a*b
        elif op == '%':
            return a%b
        elif op == '/':
            return a/b

    parser = LL1(lexer, cfg, {
        0: lambda vals: op(vals[2].op, vals[1], vals[2].operand) if vals[2].op is not None else vals[1],
        1: lambda vals: OPLST(vals[1], op(vals[3].op, vals[2], vals[3].operand) if vals[3].op is not None else vals[2]),
        2: lambda vals: OPLST(None, None),
        3: lambda vals: op(vals[2].op, vals[1], vals[2].operand) if vals[2].op is not None else vals[1],
        4: lambda vals: OPLST(vals[1], op(vals[3].op, vals[2], vals[3].operand) if vals[3].op is not None else vals[2]),
        5: lambda vals: OPLST(None, None),
        6: lambda vals: vals[2],
        7: lambda vals: ids[vals[1]]
    })

    string = "X*(A*X+B)+C"

    tree = parser.parse(string)

    tree.print_tree()

    print(tree.eval())


if __name__ == "__main__":
    test()
