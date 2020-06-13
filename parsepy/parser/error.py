from typing import Iterable

from parsepy.lexer import Token, Lexer


class CFGError(Exception):
    """

    """

    def __init__(self, msg: str):
        """

        :param msg:
        """

        super().__init__(msg)

    def __str__(self) -> str:
        """

        :return:
        """

        return "CFGError: {}".format(self.msg)


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

        super().__init__("Unknown Token: {}".format(token))
        self.token = token
