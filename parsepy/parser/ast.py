from typing import Any, Optional, Callable

from parsepy.parser.parser import AST, CFG, Token


class AST:
    """

    """

    def __init__(self, value: Any, evalfn: Optional[Callable] = None, parent: AST = None):
        """

        :param value:
        :param evalfn:
        :param parent:
        """

        self.children = []
        self.value = value
        if evalfn is None:
            if isinstance(value, CFG.NonTerm) or not self.value:
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

        vals = []
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
