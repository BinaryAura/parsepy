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
