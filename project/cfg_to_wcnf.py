from pyformlang.cfg import CFG
from pyformlang.cfg import Production


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    nullable = cfg.get_nullable_symbols()
    nf = cfg.to_normal_form()
    productions = set(nf.productions)
    for var in nullable:
        productions.add(Production(var, []))
    return CFG(nf.variables, nf.terminals, nf.start_symbol, productions)
