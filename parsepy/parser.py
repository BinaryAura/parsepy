from typing import Iterable, List, Callable, Dict

from parsepy.cfg import CFG
from parsepy.lexer import Lexer, Token


class ParserError(Exception):
    """

    """

    def __init__(self, msg: str = ""):
        """

        :param msg:
        """

        super().__init__(msg)


class SyntaxError(ParserError):
    """

    """

    def __init__(self, token: Token, msg: str):
        """

        :param token:
        :param msg:
        """

        self.token = token
        self.msg = msg

    def __str__(self):
        """

        :return:
        """

        if self.msg:
            return "Syntax Error: {}: {}".format(self.msg, self.token.loc_str())
        else:
            return "Syntax Error: {}".format(self.token.loc_str)


class UnexpToken(SyntaxError):
    """

    """

    def __init__(self, token: Token, exp: Iterable):
        """

        :param token:
        """

        super().__init__(token, "Expected token {}, found {}".format(', '.join(exp - {Lexer.EOI}), repr(token.token)))


class UnkToken(ParserError):
    """
    
    """
    
    def __init__(self, token: Token):
        """
        
        :param tok: 
        """
        
        super().__init__(token, "Unknown Token: {}".format(token))


class Parser:
    """

    """

    def __init__(self, lexer: Lexer, cfg: CFG, actions: Dict[CFG.NonTerm, Callable]):
        """

        :param lexer:
        :param cfg:
        :param actions:
        """

        nc = lexer.tokens & cfg.rules
        if nc:
            raise ParserError("Abiguous key: {}".format(nc.pop()))
        if Lexer.EOI in lexer.tokens | cfg.rules:
            raise ParserError("EOI token, {}, cannot be a key".format(Lexer.EOI))
        mt = cfg.terms - lexer.tokens
        if mt:
            raise ParserError("Terminal not defined: {}".format(mt.pop()))

        self.lexer = lexer
        self.cfg = cfg
        self.actions = actions


