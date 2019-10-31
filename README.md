parsepy
=======

Parsepy is the python port of a runtime parsing engine. It can be used to create, manipulate, and study the aspects
of a parser and lexer.

+ **Source: https://github.com/BinaryAura/parsepy
+ **Bug reports: https://github.com/BinaryAura/parsepy/issues

Lexer example
-------------

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

CFG example
-----------

```python
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

Install
-------

Install the lastest version of Parsepy:

```bash
$ pip install git+ssh://git@github.com/BinaryAura/parsepy.git
```
    
Bugs
----

Please report any bugs that you find [here](https://github.com/BinaryAura/parsepy/issues).