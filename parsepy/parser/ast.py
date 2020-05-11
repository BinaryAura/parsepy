from __future__ import annotations

from typing import Any, Optional, Callable, Union

from parsepy.lexer import Token
from parsepy.parser import CFG


class AST:
    """

    """

    def __init__(self, value: Union[CFG.Prod, Token], text: str, evalfn: Optional[Callable] = None,
                 line: int = 1, col: int = 1, file: Optional[str] = None, parent: AST = None):
        """

        :param value:
        :param evalfn:
        :param parent:
        """

        self.value = value
        self.line = line
        self.col = col
        self.text = text
        self.file = file
        self.evalfn = evalfn
        self._children = []
        self.parent = parent

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]
        for c in children:
            if not isinstance(c, AST):
                raise ValueError("children must be an list or tuple of AST objects or an AST object")
        for c in self.children:
            c._parent = None
        for c in children:
            c._parent = self
        self._children = children

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, (Token, CFG.Prod)):
            raise ValueError("value must be Token or Prod")
        self._value = value

    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, line):
        if not isinstance(line, int):
            raise ValueError("line must be an integer")
        self._line = line

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, col):
        if not isinstance(col, int):
            raise ValueError("col must be an integer")
        self._col = col

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        if file is None:
            self._file = str(type(self.text))
        elif isinstance(file, str):
            self._file = file
        else:
            raise ValueError("file must be None or str")

    @property
    def evalfn(self):
        return self._evalfn

    @evalfn.setter
    def evalfn(self, evalfn):
        if not callable(evalfn) and evalfn is not None:
            raise ValueError("evalfn must be callable")
        if evalfn is None:
            if isinstance(self.value, CFG.Prod):
                self._evalfn = lambda a: None
            else:
                self._evalfn = lambda a: self.value.token
        else:
            self._evalfn = evalfn

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if not isinstance(text, str):
            raise ValueError("text must be str")
        self._text = text

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if not isinstance(parent, AST) and parent is not None:
            raise ValueError("parent must be AST or None")
        try:
            if self.parent is not None:
                self.parent.remove_child(self)
        except AttributeError:
            pass
        if parent is not None:
            parent.add_child(self)
        else:
            self._parent = None

    def add_child(self, child: AST):
        """

        :param child:
        :return:
        """

        self.children += [child]

    def remove_child(self, child: AST):
        self.parent.children = [c for c in self.parent.children if c is not child]

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
