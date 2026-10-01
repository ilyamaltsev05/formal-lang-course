from project.adjacency_matrix_fa import AdjacencyMatrixFA
import scipy.sparse


def intersect_automata(
    automaton1: AdjacencyMatrixFA, automaton2: AdjacencyMatrixFA
) -> AdjacencyMatrixFA:
    decomposition = {
        label: scipy.sparse.kron(
            automaton1.decomposition[label],
            automaton2.decomposition[label],
            format="csr",
        )
        for label in automaton1.decomposition.keys() & automaton2.decomposition.keys()
    }
    start = {
        automaton1.state_to_idx[sa] * automaton2.dim + automaton2.state_to_idx[sb]
        for sa in automaton1.start_state_ids
        for sb in automaton2.start_state_ids
    }
    final = {
        automaton1.state_to_idx[fa] * automaton2.dim + automaton2.state_to_idx[fb]
        for fa in automaton1.final_state_ids
        for fb in automaton2.final_state_ids
    }
    return AdjacencyMatrixFA.from_decomposition(
        decomposition, automaton1.dim * automaton2.dim, start, final
    )
