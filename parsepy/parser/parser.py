from __future__ import annotations

from typing import Iterable

from os import PathLike

from parsepy.lexer import *
from parsepy.parser.cfg import CFG
from parsepy.parser import error


class Parser:
    """

    """

    def __init__(self, lexer: Lexer, cfg: CFG, actions: Dict[CFG.NonTerm, Callable] = {}):
        """

        :param lexer:
        :param cfg:
        :param actions:
        """

        nc = lexer.tokens & cfg.rules
        if nc:
            raise error.ParserError("Abiguous key: {}".format(nc.pop()))
        if Lexer.EOI in lexer.tokens | cfg.rules:
            raise error.ParserError("EOI token, {}, cannot be a key".format(Lexer.EOI))
        mt = cfg.terms - lexer.tokens
        if mt:
            raise error.ParserError("Terminal not defined: {}".format(mt.pop()))

        self.lexer = lexer
        self.cfg = cfg
        self.actions = actions

    def get_tokens(self, string: Iterable, file: PathLike = "") -> Lexer.Iter:
        """

        :param string:
        :return:
        """

        if not file:
            file = repr(string.__class__)

        if isinstance(string, Iterable):
            t_iter = self.lexer.tokenize(string, file)
        else:
            raise ValueError("string must be Iterable, found {}".format(string.__class__))
        return t_iter

    def get_tokens_from_file(self, path: PathLike) -> Lexer.Iter:
        """

        :param path:
        :return:
        """

        return self.lexer.tokenize_file(path)
