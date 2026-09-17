from dataclasses import dataclass
from pathlib import Path
from typing import Any
import cfpq_data
import networkx as nx
import pydot


@dataclass
class GraphData:
    vertices: int
    edges: int
    labels: Any


def load_graph_data(graph_name: str) -> GraphData | None:
    try:
        graph_path = cfpq_data.download(graph_name)
        graph = cfpq_data.graph_from_csv(graph_path)
        return GraphData(
            graph.number_of_nodes(),
            graph.number_of_edges(),
            set(cfpq_data.get_sorted_labels(graph)),
        )
    except FileNotFoundError:
        return None


def dump_two_cycles_graph(
    first_cycle_size: int, second_cycle_size: int, labels: tuple[str, str], output: Path
) -> None:
    g = cfpq_data.labeled_two_cycles_graph(
        first_cycle_size, second_cycle_size, labels=labels
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    pydot_graph = nx.nx_pydot.to_pydot(g)
    pydot_graph.write(output)
