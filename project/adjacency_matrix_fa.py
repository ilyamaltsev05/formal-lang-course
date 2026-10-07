from typing import Iterable
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, Symbol
import networkx as nx
import scipy.sparse


class AdjacencyMatrixFA:
    def __init__(self, automaton: NondeterministicFiniteAutomaton) -> None:
        networkx_automaton = automaton.to_networkx()
        self.states = list(networkx_automaton.nodes)
        self.state_to_idx = {state: idx for idx, state in enumerate(self.states)}
        self.dim = len(networkx_automaton.nodes)
        self.start_state_ids = {
            n
            for n, v in nx.get_node_attributes(networkx_automaton, "is_start").items()
            if v
        }
        self.final_state_ids = {
            n
            for n, v in nx.get_node_attributes(networkx_automaton, "is_final").items()
            if v
        }
        self.all_labels = {
            label
            for _, _, label in networkx_automaton.edges(data="label")
            if label is not None and label != "ɛ"
        }
        self.decomposition = dict()
        for label in self.all_labels:
            edges = [
                (self.state_to_idx[from_node], self.state_to_idx[to_node])
                for from_node, to_node, edge_label in networkx_automaton.edges(
                    data="label"
                )
                if edge_label == label
            ]
            rows = [row for row, _ in edges]
            cols = [col for _, col in edges]
            data = [True] * len(edges)
            self.decomposition[label] = scipy.sparse.csr_matrix(
                (data, (rows, cols)), (self.dim, self.dim), dtype=bool
            )

    @classmethod
    def from_decomposition(cls, decomposition, dim, start_state_ids, final_state_ids):
        obj = cls.__new__(cls)
        obj.dim = dim
        obj.states = list(range(dim))
        obj.state_to_idx = {state: state for state in obj.states}
        obj.start_state_ids = start_state_ids
        obj.final_state_ids = final_state_ids
        obj.decomposition = decomposition
        obj.all_labels = set(decomposition.keys())
        return obj

    def accepts(self, word: Iterable[Symbol]) -> bool:
        cur = scipy.sparse.csr_matrix((1, self.dim), dtype=bool)
        for s in self.start_state_ids:
            cur[0, self.state_to_idx[s]] = True

        for symbol in word:
            mat = self.decomposition.get(str(symbol))
            if mat is None:
                return False
            cur = (cur @ mat) > 0

        return any(cur[0, self.state_to_idx[f]] for f in self.final_state_ids)

    def is_empty(self) -> bool:
        reachability = scipy.sparse.csr_matrix((self.dim, self.dim), dtype=bool)
        for mat in self.decomposition.values():
            reachability = reachability + mat
        reachability = reachability + scipy.sparse.identity(self.dim, dtype=bool)

        while True:
            closure = (reachability @ reachability) > 0
            if closure.nnz == reachability.nnz:
                break
            reachability = closure

        return not any(
            reachability[self.state_to_idx[s], self.state_to_idx[f]]
            for s in self.start_state_ids
            for f in self.final_state_ids
        )
