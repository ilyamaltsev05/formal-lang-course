import networkx as nx
import scipy.sparse
from pyformlang.cfg import CFG, Terminal

from project.cfg_to_wcnf import cfg_to_weak_normal_form


def matrix_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    cfg = cfg_to_weak_normal_form(cfg)

    nodes = list(graph.nodes)
    index = {node: i for i, node in enumerate(nodes)}
    dim = len(nodes)
    start_nodes = start_nodes or set(nodes)
    final_nodes = final_nodes or set(nodes)

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

    label_edges = {}
    for source, target, data in graph.edges(data=True):
        rows, cols = label_edges.setdefault(data.get("label"), ([], []))
        rows.append(index[source])
        cols.append(index[target])
    adjacencies = {
        label: scipy.sparse.csr_matrix(
            ([True] * len(rows), (rows, cols)), shape=(dim, dim), dtype=bool
        )
        for label, (rows, cols) in label_edges.items()
    }

    matrices = {}

    def matrix_of(nonterminal):
        if nonterminal not in matrices:
            matrices[nonterminal] = scipy.sparse.csr_matrix((dim, dim), dtype=bool)
        return matrices[nonterminal]

    for label, heads in terminal_rules.items():
        for head in heads:
            if label in adjacencies:
                matrices[head] = matrix_of(head) + adjacencies[label]

    for head in epsilon_rules:
        matrices[head] = matrix_of(head) + scipy.sparse.identity(dim, dtype=bool)

    changed = True
    while changed:
        changed = False
        for (left, right), heads in binary_rules.items():
            product = matrix_of(left) @ matrix_of(right)
            for head in heads:
                added = (product > matrix_of(head)).tocsr()
                if added.nnz:
                    matrices[head] = (matrix_of(head) + added) > 0
                    changed = True

    if cfg.start_symbol not in matrices:
        return set()

    reachability = matrices[cfg.start_symbol]
    return {
        (source, target)
        for source in start_nodes
        for target in final_nodes
        if reachability[index[source], index[target]]
    }
