from collections import deque

import networkx as nx
from pyformlang.cfg import CFG, Terminal

from project.cfg_to_wcnf import cfg_to_weak_normal_form


def hellings_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    cfg = cfg_to_weak_normal_form(cfg)

    nodes = set(graph.nodes)
    start_nodes = start_nodes or nodes
    final_nodes = final_nodes or nodes

    terminal_rules = {}
    binary_rules = {}
    epsilon_rules = []
    for production in cfg.productions:
        head, body = production.head, production.body
        if len(body) == 0:
            epsilon_rules.append(head)
        elif len(body) == 2:
            binary_rules.setdefault(tuple(body), []).append(head)
        elif len(body) == 1 and isinstance(body[0], Terminal):
            terminal_rules.setdefault(body[0].value, []).append(head)

    result = set()
    edges = []
    queue = deque()

    def add(nonterminal, source, target):
        triple = (nonterminal, source, target)
        if triple not in result:
            result.add(triple)
            edges.append(triple)
            queue.append(triple)

    for source, target, data in graph.edges(data=True):
        for nonterminal in terminal_rules.get(data.get("label"), ()):
            add(nonterminal, source, target)

    for nonterminal in epsilon_rules:
        for node in nodes:
            add(nonterminal, node, node)

    while queue:
        nonterminal, source, target = queue.popleft()
        for other, other_source, other_target in list(edges):
            if other_target == source:
                for head in binary_rules.get((other, nonterminal), ()):
                    add(head, other_source, target)
            if other_source == target:
                for head in binary_rules.get((nonterminal, other), ()):
                    add(head, source, other_target)

    start_symbol = cfg.start_symbol
    return {
        (source, target)
        for nonterminal, source, target in result
        if nonterminal == start_symbol
        and source in start_nodes
        and target in final_nodes
    }
