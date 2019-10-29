"""
@author: BinaryAura <jadunker@hotmail.com>
"""

from __future__ import annotations
from typing import Hashable, Dict, Any, Optional, Tuple, Callable, Iterator
import re


class LexerError(Exception):
    """

    """

    def __init__(self, msg):
        """
        """

        super().__init__(msg)


class RegexError(LexerError):
    """

    """

    def __init__(self, msg, token, regex, pos):
        """

        :param msg:
        :param token:
        :param regex:
        :param pos:
        """

        self.token = token
        self.pattern = regex
        self.pos = pos
        super().__init__(msg)

    def __str__(self) -> str:
        """

        :return:
        """

        return "RegexError: {}: {} = {} pos: {}".format(self.msg, self.token, self.pattern, self.pos)


class TokenError(LexerError):
    """

    """

    def __init__(self, msg, token):
        """

        :param msg:
        :param token:
        """

        self.token = token.token
        self.col = token.col
        self.line = token.line

    def __str__(self):
        """

        :return:
        """

        return "Unknown Token: {}:{}".format(self.line, self.col)


class Token:
    """

    """

    def __init__(self, ttype: Hashable, token: str, line: int = 1, col: int = 1, file: Optional[str] = None):
        """

        :param ttype:
        :param token:
        :param line:
        :param col:
        """

        self.type = ttype
        self.token = token
        self.line = line
        self.col = col
        self.file = file

    def loc_str(self):
        if self.file:
            return  "{}:{}:{}".format(self.file, self.line, self.col)
        else:
            return "{}:{}".format(self.line, self.col)

    def __eq__(self, other) -> bool:
        """

        :param other:
        :return:
        """

        return self.type == other.type and self.token == other.token

    def __ne__(self, other) -> bool:
        """

        :param other:
        :return:
        """

        return self.type != other.type or self.token != other.token

    def __str__(self) -> str:
        """

        :return:
        """

        return self.token

    def __repr__(self) -> str:
        """

        :return:
        """

        return "{}({})".format(self.type, repr(self.token))


class Lexer:
    """

    """

    EOI = "EOI"
    UNK = "unknown"

    class Iter:
        """

        """

        def __init__(self, lexer, str_in: str):
            """

            :param lexer:
            :param str_in:
            """

            self.lexer = lexer
            self.str_in = str_in
            self.line_idx = [i for i in range(len(str_in)) if i == 0 or str_in[i - 1] == '\n']
            self.n = 0
            self.stop = False

        def __iter__(self) -> Lexer.Iter:
            """

            :return:
            """

            self.n = 0
            self.stop = False
            return self

        def __next__(self) -> Token:
            """

            :return:
            """

            if self.n >= len(self.str_in):
                if self.stop:
                    raise StopIteration
                else:
                    self.stop = True
                    t = Token(Lexer.EOI, None, len(self.line_idx), self.n - self.line_idx[-1])
                    return t
            token = None
            while token is None:
                ttype, token, length = self.lexer.get_token(self.str_in[self.n])
                if token is not None:
                    line = self.line_idx.index(max(i for i in self.line_idx if i <= self.n))
                    col = self.n - self.line_idx[line]
                    out = Token(ttype, token, line + 1, col + 1)
                self.n += length
            return out

    def __init__(self, tokens: Optional[Dict] = None, actions: Optional[Dict[Hashable, Callable[[str], Any]]] = None):
        """

        :param tokens:
        :param actions:
        """

        if actions is None:
            actions = {}
        if tokens is None:
            tokens = {}
        self._tokens = tokens
        for token, regex in tokens.items():
            try:
                self._tokens[token] = re.compile(regex)
            except re.error as err:
                raise Lexer.Error(err.msg, token, err.pattern, err.pos)
        self.actions = actions

    @property
    def tokens(self) -> Iterator[str]:
        """

        :return:
        """

        return set(self._tokens.keys())

    def __len__(self) -> int:
        """

        :return:
        """

        return len(self.tokens)

    def get_token(self, string: str) -> Tuple:
        """

        :param string:
        :return:
        """

        greedy = (Lexer.UNK, string[0])
        for token, regex in self._tokens.items():
            match = regex.match(string)
            if match is not None:
                if greedy[0] == Lexer.UNK or len(greedy[1]) < len(match[0]):
                    greedy = (token, match[0])
        try:
            return greedy[0], self.actions[greedy[0]](greedy[1]), len(greedy[1])
        except KeyError:
            return greedy[0], greedy[1], len(greedy[1])

    def tokenize(self, str_in: str) -> Lexer.Iter:
        """

        :param str_in:
        :return:
        """

        return Lexer.Iter(self, str_in)


def test():
    import sys

    tokreg = {
        "t_plus": r"\+",
        "t_mult": r"\*",
        "t_leftp": r"\(",
        "t_rightp": r"\)",
        "t_id": r"[A-Za-z_]\w*",
        "t_ws": r"[ \t]+",
    }

    act = {"t_ws": lambda a: None}
    try:
        lexer = Lexer(tokreg, act)

        for tok in lexer.tokenize('A*x*x + B*x + C'):
            print(repr(tok))
    except LexerError as err:
        print(str(err), file=sys.stderr)


if __name__ == "__main__":
    test()
