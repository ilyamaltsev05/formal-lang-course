from typing import Set

from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    r = Regex(regex)
    nfa = r.to_epsilon_nfa()
    assert nfa is not None
    dfa = nfa.to_deterministic().minimize()
    return dfa


def graph_to_nfa(
    graph: MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:
    a = NondeterministicFiniteAutomaton.from_networkx(graph)
    match len(start_states):
        case 0:
            for v in graph.nodes:
                a.add_start_state(v)
        case _:
            for s in start_states:
                a.add_start_state(s)
    match len(final_states):
        case 0:
            for v in graph.nodes:
                a.add_final_state(v)
        case _:
            for f in final_states:
                a.add_final_state(f)
    return a.remove_epsilon_transitions()
