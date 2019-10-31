import parsepy

cfg = parsepy.parser.CFG.parse("""E  -> T E'
E' -> t_mult T E' | \u03B5
T  -> F T'
T' -> t_plus F T' |
F  -> t_lparen E t_rparen | t_id""")

print(cfg.first("E'"))

print(cfg.follow('F'))