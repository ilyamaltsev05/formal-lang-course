from collections import deque

import networkx as nx
from pyformlang import rsa


def gll_based_cfpq(
    rsm: rsa.RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    nodes = set(graph.nodes)
    start_nodes = start_nodes or nodes
    final_nodes = final_nodes or nodes

    box_start = {}
    transitions = {}
    final_states = set()
    initial_label = str(rsm.initial_label)
    for label, box in rsm.boxes.items():
        box_label = str(label)
        dfa = box.dfa
        box_start[box_label] = (box_label, dfa.start_state)
        for state in dfa.final_states:
            final_states.add((box_label, state))
        for state, edges in dfa.to_dict().items():
            transitions[(box_label, state)] = [
                (str(symbol), (box_label, target)) for symbol, target in edges.items()
            ]

    out_edges = {}
    for source, target, data in graph.edges(data=True):
        label = data.get("label")
        if label is None:
            continue
        out_edges.setdefault(source, {}).setdefault(label, []).append(target)

    initial_start = box_start[initial_label]
    initial_finals = {state for state in final_states if state[0] == initial_label}

    result = set()
    for start in start_nodes:
        worklist = deque()
        seen = set()
        parents = {}
        popped = {}
        accepted = set()

        def add_descriptor(top, state, vertex):
            descriptor = (top, state, vertex)
            if descriptor not in seen:
                seen.add(descriptor)
                worklist.append(descriptor)

        def add_parent(node, parent):
            node_parents = parents.setdefault(node, set())
            if parent in node_parents:
                return
            node_parents.add(parent)
            for vertex in popped.get(node, ()):
                add_descriptor(parent, node[1], vertex)

        add_descriptor(None, initial_start, start)

        while worklist:
            top, state, vertex = worklist.popleft()

            for symbol, target in transitions.get(state, ()):
                if symbol in box_start:
                    node = (symbol, target, vertex)
                    add_parent(node, top)
                    add_descriptor(node, box_start[symbol], vertex)
                else:
                    for next_vertex in out_edges.get(vertex, {}).get(symbol, ()):
                        add_descriptor(top, target, next_vertex)

            if state in final_states:
                if top is None:
                    if state in initial_finals:
                        accepted.add(vertex)
                else:
                    popped.setdefault(top, set()).add(vertex)
                    for parent in parents.get(top, ()):
                        add_descriptor(parent, top[1], vertex)

        result.update((start, final) for final in final_nodes if final in accepted)

    return result
