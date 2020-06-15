parsepy
=======

Parsepy is the python port of a runtime parsing engine. It can be used to create, manipulate, and study the aspects
of a parser and lexer. It takes python re regex strings as token definitions and
CFG string as a definition for a grammar. Both the lexer and the parser are capable of
accepting functions that define what how to evaluate a token or production.

The parsepy library functions on a modular basis by splitting the Lexicon 
up from the Grammar and the Parser. 

+ **Source: https://github.com/BinaryAura/parsepy
+ **Bug reports: https://github.com/BinaryAura/parsepy/issues

Install
-------

Install the lastest version of Parsepy:

```bash
$ pip install git+ssh://git@github.com/BinaryAura/parsepy.git
```

Lexer
-----

The Lexer class handles the atomic tokens within a
string to be parsed (in 'C/C++' this would be 'if', 'else' , '{', numbers,
identifiers, operators, etc). It does this via determining the longest matching [regular
expression](https://www.w3schools.com/python/python_regex.asp) defined token. If no token
matches, a default "unknown" token is given.

Lexer can take advantage of pythonic [iterators](https://wiki.python.org/moin/Iterator)
and "for" by using tokenize(), which returns an iterator to determine the tokens in the
given string. This iterator returns a Token object when using the [next()](https://www.w3schools.com/python/ref_func_next.asp)
builtin.

Lexer also can give a defined value to a token via functions mapped to the token names.
By default, each token has a function that returns the string that matched the regex.
This value is stored in Token's value field. However, if the function evaluates to
'None', the token is skipped and will not be present in the tokenize() iterator.

### Example

```python
>>> import parsepy
>>> lexer = parsepy.lexer.Lexer({
...     "t_plus": r"\+",
...     "t_mult": r"\*",
...     "t_lparen": r"\(",
...     "t_rparen": r"\)",
...     "t_id": r"[A-Za-z_]\w*"
... })
>>> for token in lexer.tokenize("A*X*X+B*X+C"):
...     print(repr(token))
t_id('A')
t_mult('*')
t_id('X')
t_mult('*')
t_id('X')
t_plus('+')
t_id('B')
t_mult('*')
t_id('X')
t_plus('+')
t_id('C')
EOI(None)
```

CFG
---

The CFG class defines a [context free grammar](https://www.tutorialspoint.com/automata_theory/context_free_grammar_introduction.htm)
and handles [FIRST](https://www.geeksforgeeks.org/first-set-in-syntax-analysis/),
[FOLLOW](https://www.geeksforgeeks.org/follow-set-in-syntax-analysis/?ref=lbp), and 
[SELECT](https://stackoverflow.com/questions/46816247/method-to-calculate-predict-set-of-a-grammar-production-in-recursive-descent-par)
(a.k.a. PREDICT) sets.

CFG contains a collection of Prod[uction] objects, which define a production in a grammar,
and a starting symbol. The items within a Prod object are either Non-Term[inal] or str (Terminal)
objects. CFG also has a parse() function that takes a str and returns a CFG.

The syntax is
```Non-Term -> item ... [| item ...] ...```. ```\u03B5``` can be used to represent epsilon
as well as a not listing any items in a production ```|``` separates productions for the same Non-Terminal on the same line.


### Example

```python
>>> import parsepy
>>> cfg = parsepy.parser.CFG.parse("""E -> T E'
... E' -> t_mult T E' | \u03B5
... T -> F T'
... T' -> t_plus F T' |
... F -> t_lparen E t_rparen | t_id""")
>>> cfg.first("E'")
{None, 't_mult'}
>>> cfg.follow('F')
{'EOI', 't_plus', 't_rparen', 't_mult'}
```

Parser
------

parsepy supports multiple types of parsers through inheritance of the Parser class. Every parser
object requires three things: a Lexer, a CFG, and a map of functions to [Non-Term]inals. The
functions of the map will be passed a list, of which the 0 index will be the AST node for the
Production or Token being evaluated, and the rest of the list are the evaluations of the child
nodes.

Please note that the Parser class is not meant as an abstract class and not to be used directly,
rather programs should use a class that derives Parser. When extending Parser, setup procedures
should be preformed in '\_\_init\_\_()' following ```super().__init__(lexer, cfg, actions)```
and a 'parse()' function should be defined to return an accurate
[abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree),
or AST, of the 'text' passed to the function starting at the Non-Terminal specified by 'start'
through the Lexer and CFG. The value field of the AST nodes should be the Non-Terminals and Terminals found
in the derivation, where the Terminals are the leaves. The evalfn field should be the relevent
function for the AST node being evaluated. The line, col, and file fields give location information
for the AST node and the text field is the raw text which this AST node refers to.

Currently, only an LL(1) Parsing Table parser is implemented as the LL1 class.

### Example

```python
>>> import parsepy
>>> from collections import namedtuple
>>> 
>>> tokreg = {
...     "t_plus": r"\+",
...     "t_mult": r"\*",
...     "t_lparen": r"\(",
...     "t_rparen": r"\)",
...     "t_id": r"[A-Za-z_]\w*",
...     "t_ws": r"[ \t]+",
... }

>>> act = {"t_ws": lambda a: None}

>>> lexer = Lexer(tokreg, act)

>>> cfg_str = """E  -> T E'
...             E' -> t_mult T E' | \u03B5
...             T  -> F T'
...             T' -> t_plus F T' |
...             F  -> t_lparen E t_rparen | t_id"""

>>> cfg = CFG.parse(cfg_str)

>>> ids = {'A': 1, 'B': 2, 'X': 4, 'C': 0}

>>> OPLST = namedtuple('OPLST', 'op operand')

>>> def op(op, a, b):
...     if op == '+':
...         return a + b
...     elif op == '-':
...         return a-b
...     elif op == '*':
...         return a*b
...     elif op == '%':
...         return a%b
...     elif op == '/':
...         return a/b

>>> parser = LL1(lexer, cfg, {
...     0: lambda vals: op(vals[2].op, vals[1], vals[2].operand) if vals[2].op is not None else vals[1],
...     1: lambda vals: OPLST(vals[1], op(vals[3].op, vals[2], vals[3].operand) if vals[3].op is not None else vals[2]),
...     2: lambda vals: OPLST(None, None),
...     3: lambda vals: op(vals[2].op, vals[1], vals[2].operand) if vals[2].op is not None else vals[1],
...     4: lambda vals: OPLST(vals[1], op(vals[3].op, vals[2], vals[3].operand) if vals[3].op is not None else vals[2]),
...     5: lambda vals: OPLST(None, None),
...     6: lambda vals: vals[2],
...     7: lambda vals: ids[vals[1]]
... })
>>> string = "X*(A*X+B)+C"
>>> print(tree.eval())
```

Errors
------

parsepy implements some errors to better understand what goes wrong during parsing and lexing.
Of these are:
- LexerError: Error when lexing a string
- RegexError: LexerError when a regex definition fails regex syntax
- CFGError: Error when constructing a CFG object
- ParserError: Error when parsing a string
- SyntaxError: ParserError when the text doesn't match the CFG
- UnexpToken: SyntaxError when a Token doesn't match the CFG
- UnkToken: ParserError when a unrecognized token is found

Bugs
----

Please report any bugs that you find [here](https://github.com/BinaryAura/parsepy/issues).
