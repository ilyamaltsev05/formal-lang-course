from dataclasses import dataclass
import project.task01 as tsk01


@dataclass
class wc:
    vertices = 332
    edges = 269
    labels = set(["a", "d"])


@dataclass
class univ:
    vertices = 179
    edges = 293
    labels = set(
        [
            "type",
            "label",
            "subClassOf",
            "domain",
            "range",
            "first",
            "rest",
            "someValuesFrom",
            "onProperty",
            "intersectionOf",
            "subPropertyOf",
            "inverseOf",
            "versionInfo",
            "comment",
        ]
    )


@dataclass
class gzip:
    vertices = 2687
    edges = 2293
    labels = set(["a", "d"])


class TestLoadNonExistingGraph:
    def setup_method(self):
        self.failed_graph = tsk01.load_graph_data("graph_monte_cristo")

    def test_graphs_not_found(self):
        assert self.failed_graph is None


class TestLoadGraph:
    def setup_method(self):
        self.wc = tsk01.load_graph_data("wc")
        self.univ = tsk01.load_graph_data("univ")
        self.gzip = tsk01.load_graph_data("gzip")

    def test_wc(self):
        assert not self.wc is None
        assert self.wc.vertices == wc.vertices
        assert self.wc.edges == wc.edges
        assert self.wc.labels == wc.labels

    def test_univ(self):
        assert not self.wc is None
        assert self.wc.vertices == wc.vertices
        assert self.wc.edges == wc.edges
        assert self.wc.labels == wc.labels

    def test_gzip(self):
        assert not self.wc is None
        assert self.wc.vertices == wc.vertices
        assert self.wc.edges == wc.edges
        assert self.wc.labels == wc.labels
