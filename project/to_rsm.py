from pyformlang import cfg
from pyformlang import rsa
from pyformlang.finite_automaton import Symbol


def cfg_to_rsm(cfg: cfg.CFG) -> rsa.RecursiveAutomaton:
    s = cfg.start_symbol
    text = cfg.to_text()
    return rsa.RecursiveAutomaton().from_text(text, Symbol(s.to_text()))


def ebnf_to_rsm(ebnf: str) -> rsa.RecursiveAutomaton:
    return rsa.RecursiveAutomaton().from_text(ebnf)
