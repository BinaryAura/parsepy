# parsepy

Parsepy is the python port of a runtime parsing engine. It can be used to create, manipulate, and study the aspects
of a parser and lexer.

- **Source: https://github.com/BinaryAura/parsepy
- **Bug reports: https://github.com/BinaryAura/parsepy/issues

## Simple example

.. code:: python

    >>> import parsepy
    >>> lexer = parsepy.lexer.Lexer({
    ...     "t_plus": r"\+",
    ...     "t_mult": r"\*",
    ...     "t_lparen": r"\(",
    ...     "t_rparen": r"\)",
    ...     "t_id": r"[A-Za-z_]\w*"
    ... })
    >>> cfg = parsepy.parser.CFG.parse("""E -> T E'
    ... E' -> t_mult T E' | \u03B5
    ... T -> F T'
    ... T' -> t_plus F T' |
    ... F -> t_lparen E t_rparen | t_id""")
    >>> parser = parsepy.parser.LL1(lexer, cfg)
    >>> parser.tree("A+B*X").print_tree()
