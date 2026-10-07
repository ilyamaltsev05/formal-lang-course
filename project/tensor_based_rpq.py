from networkx import MultiDiGraph
from project.to_finite_automaton_converters import regex_to_dfa, graph_to_nfa
from project.adjacency_matrix_fa import AdjacencyMatrixFA
from project.automata_intersection import intersect_automata
import scipy.sparse


def tensor_based_rpq(
    regex: str, graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int]
) -> set[tuple[int, int]]:
    nodes = set(graph.nodes)
    start_nodes = start_nodes or nodes
    final_nodes = final_nodes or nodes
    query = AdjacencyMatrixFA(regex_to_dfa(regex))
    target = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))
    intersection = intersect_automata(query, target)

    dim = intersection.dim
    adjacency = scipy.sparse.csr_matrix((dim, dim), dtype=bool)
    for matrix in intersection.decomposition.values():
        adjacency = adjacency + matrix
    adjacency = (adjacency + scipy.sparse.identity(dim, dtype=bool)) > 0

    reachability = adjacency
    while True:
        closure = (reachability @ reachability) > 0
        if closure.nnz == reachability.nnz:
            break
        reachability = closure

    target_dim = target.dim
    result = set()
    for start in start_nodes:
        for final in final_nodes:
            for query_start in query.start_state_ids:
                for query_final in query.final_state_ids:
                    from_state = (
                        query.state_to_idx[query_start] * target_dim
                        + target.state_to_idx[start]
                    )
                    to_state = (
                        query.state_to_idx[query_final] * target_dim
                        + target.state_to_idx[final]
                    )
                    if reachability[from_state, to_state]:
                        result.add((start, final))
                        break
    return result
