import project.task01 as tsk01
import networkx as nx
from pathlib import Path


class TestIsomorphismAfterDump:
    def setup_method(self):
        tsk01.dump_two_cycles_graph(1, 2, ("x", "y"), Path("./tmp/1x2.dot"))
        tsk01.dump_two_cycles_graph(10, 100, ("first label", "second label"), Path("./tmp/10x100.dot"))


    def reference_graph(self, first_cycle_size: int, second_cycle_size: int, labels: tuple[str, str]) -> nx.Graph:
        c1 = nx.cycle_graph(first_cycle_size + 1)
        c2 = nx.cycle_graph([i + first_cycle_size if i != 0 else 0 for i in range(second_cycle_size + 1)])
        nx.set_edge_attributes(c1, name="label", values=labels[0])
        nx.set_edge_attributes(c2, name="label", values=labels[1])
        g = nx.compose(c1, c2)
        return g


    def test_isomorphism_of_small_graph(self):
        g = nx.Graph(nx.nx_pydot.read_dot("./tmp/1x2.dot"))
        ref = self.reference_graph(1, 2, ("x", "y"))
        assert nx.is_isomorphic(g, ref)


    def test_isomorphism_of_bigger_graph(self):
        g = nx.Graph(nx.nx_pydot.read_dot("./tmp/10x100.dot"))
        ref = self.reference_graph(10, 100, ("first label", "second label"))
        assert nx.is_isomorphic(g, ref)


    def teardown_method(self):
        dir = Path("./tmp")
        if dir.exists() and dir.is_dir():
            for item in sorted(dir.rglob("*"), reverse=True):
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()

        dir.rmdir()
