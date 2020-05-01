from __future__ import annotations

from typing import Any, Optional, Callable, Union

from parsepy.lexer import Token
from parsepy.parser import CFG


class AST:
    """

    """

    def __init__(self, value: Union[CFG.Prod, Token], evalfn: Optional[Callable] = None, line: int = 1, col: int = 1, file: Optional[str] = None, parent: AST = None):
        """

        :param value:
        :param evalfn:
        :param parent:
        """

        self.children = []
        self.value = value
        self.line = line
        self.col = col
        self.raw = ''
        self.idx = 0
        if file is None:
            self.file = ""
        else:
            self.file = file
        if evalfn is None:
            if isinstance(value, CFG.Prod) or not self.value:
                self.evalfn = lambda a: None
            else:
                self.evalfn = lambda a: self.value.token
        else:
            self.evalfn = evalfn
        self.parent = parent

    def add_child(self, child: AST):
        """

        :param child:
        :return:
        """

        self.children += [child]
        self.children[-1].parent = self

    def eval(self):
        """

        :return:
        """

        vals = [self]
        for c in self:
            vals += [c.eval()]
        ans = self.evalfn(vals)
        return self.evalfn(vals)

    def __getitem__(self, idx: int) -> AST:
        """

        :param idx:
        :return:
        """

        return self.children[idx]

    def __iter__(self):
        """

        :return:
        """

        return iter(self.children)

    def __eq__(self, other):
        """

        :param other:
        :return:
        """

        if self.value != other.value:
            return False

        for n, child in enumerate(self.children):
            try:
                if child != other[n]:
                    return False
            except IndexError:
                return False

        return True

    def __ne__(self, other):
        """

        :param other:
        :return:
        """

        return not self == other

    def print_tree(self, indent=""):
        middle = len(self.children)//2
        a, b = self.children[:middle], self.children[middle:]
        for child in a:
            child.print_tree(indent+"  ")
        print("{}{}".format(indent, repr(self.value) if isinstance(self.value, Token) else str(self.value)))
        for child in b:
            child.print_tree(indent+"  ")
