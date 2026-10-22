from networkx import MultiDiGraph
import scipy.sparse
from project.to_finite_automaton_converters import regex_to_dfa, graph_to_nfa
from project.adjacency_matrix_fa import AdjacencyMatrixFA


def ms_bfs_based_rpq(
    regex: str, graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int]
) -> set[tuple[int, int]]:
    query = AdjacencyMatrixFA(regex_to_dfa(regex))
    target = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))

    nodes = set(graph.nodes)
    start_nodes = start_nodes or nodes
    final_nodes = final_nodes or nodes

    query_dim = query.dim
    graph_dim = target.dim

    transitions = [
        (target.decomposition[label], query.decomposition[label])
        for label in target.decomposition.keys() & query.decomposition.keys()
    ]

    query_start_cols = [query.state_to_idx[s] for s in query.start_state_ids]
    query_final_cols = [query.state_to_idx[f] for f in query.final_state_ids]

    frontiers = {}
    visitations = {}
    for start in start_nodes:
        frontier = scipy.sparse.csr_matrix((graph_dim, query_dim), dtype=bool)
        row = target.state_to_idx[start]
        for col in query_start_cols:
            frontier[row, col] = True
        frontier = frontier.tocsr()
        frontiers[start] = frontier
        visitations[start] = frontier.copy()

    while True:
        changed = False
        for start in start_nodes:
            frontier = frontiers[start]
            if frontier.nnz == 0:
                continue

            new_frontier = scipy.sparse.csr_matrix((graph_dim, query_dim), dtype=bool)
            for graph_matrix, query_matrix in transitions:
                new_frontier = new_frontier + graph_matrix.T @ (frontier @ query_matrix)
            new_frontier = (new_frontier > 0).tocsr()

            visited = visitations[start]
            added = (new_frontier > visited).tocsr()
            if added.nnz:
                changed = True
                visitations[start] = (visited + added) > 0
            frontiers[start] = added

        if not changed:
            break

    result = set()
    for start in start_nodes:
        visited = visitations[start]
        for final in final_nodes:
            row = target.state_to_idx[final]
            if any(visited[row, col] for col in query_final_cols):
                result.add((start, final))

    return result
