import networkx as nx
import scipy.sparse
from pyformlang import rsa

from project.adjacency_matrix_fa import AdjacencyMatrixFA
from project.to_finite_automaton_converters import graph_to_nfa


def _transitive_closure(adjacency):
    dim = adjacency.shape[0]
    reachability = (adjacency + scipy.sparse.identity(dim, dtype=bool)) > 0
    while True:
        closure = (reachability @ reachability) > 0
        if closure.nnz == reachability.nnz:
            return reachability
        reachability = closure


def tensor_based_cfpq(
    rsm: rsa.RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    nodes = set(graph.nodes)
    start_nodes = start_nodes or nodes
    final_nodes = final_nodes or nodes

    graph_automaton = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))
    index = graph_automaton.state_to_idx
    dim = graph_automaton.dim

    def empty_graph_matrix():
        return scipy.sparse.csr_matrix((dim, dim), dtype=bool)

    graph_matrices = {
        str(label): matrix for label, matrix in graph_automaton.decomposition.items()
    }
    for label in rsm.labels:
        graph_matrices.setdefault(str(label), empty_graph_matrix())

    box_automata = [
        (str(label), AdjacencyMatrixFA(box.dfa)) for label, box in rsm.boxes.items()
    ]
    symbols = set()
    for _, automaton in box_automata:
        symbols.update(automaton.decomposition.keys())

    rsm_matrices = {}
    for symbol in symbols:
        blocks = [
            automaton.decomposition.get(
                symbol,
                scipy.sparse.csr_matrix((automaton.dim, automaton.dim), dtype=bool),
            )
            for _, automaton in box_automata
        ]
        rsm_matrices[symbol] = scipy.sparse.block_diag(blocks, format="csr")

    box_info = {}
    offset = 0
    for label, automaton in box_automata:
        start_state = (
            offset + automaton.state_to_idx[next(iter(automaton.start_state_ids))]
        )
        final_states = {
            offset + automaton.state_to_idx[state]
            for state in automaton.final_state_ids
        }
        box_info[label] = (start_state, final_states)
        offset += automaton.dim

    states_count = sum(automaton.dim for _, automaton in box_automata)
    if states_count == 0 or dim == 0:
        return set()

    while True:
        product = scipy.sparse.csr_matrix(
            (dim * states_count, dim * states_count), dtype=bool
        )
        for symbol, rsm_matrix in rsm_matrices.items():
            graph_matrix = graph_matrices.get(symbol)
            if graph_matrix is None or graph_matrix.nnz == 0:
                continue
            product = product + scipy.sparse.kron(
                graph_matrix, rsm_matrix, format="csr"
            )
        product = (product > 0).tocsr()

        reachability = _transitive_closure(product)

        changed = False
        for label, (start_state, final_states) in box_info.items():
            to_add = empty_graph_matrix()
            for final_state in final_states:
                to_add = (
                    to_add
                    + reachability[start_state::states_count, final_state::states_count]
                )
            to_add = (to_add > 0).tocsr()

            added = (to_add > graph_matrices[label]).tocsr()
            if added.nnz:
                graph_matrices[label] = (graph_matrices[label] + added) > 0
                changed = True

        if not changed:
            break

    start_label = graph_matrices[str(rsm.initial_label)]
    return {
        (source, target)
        for source in start_nodes
        for target in final_nodes
        if start_label[index[source], index[target]]
    }
