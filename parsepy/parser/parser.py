from __future__ import annotations

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
