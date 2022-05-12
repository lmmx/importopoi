from pathlib import Path
from typing import Iterator

import graph_tool as gt
from graph_tool.draw import graph_draw
from import_deps import ModuleSet

from .log_utils import set_up_logging

__all__ = ["DirectedModuleGraph", "draw_directed_graph"]

logger = set_up_logging(__name__)


class DirectedModuleGraph:
    def __init__(self, path: str):
        self.path = path
        self.adjacencies: dict[str, set[str]] = self.get_adjacency_list()
        self.adj_n = self.numeric_adjacencies()
        # The 'adjacency list' is a list of imports, so reverse the edges,
        # or else you'd represent "imports from" by an outbound edge (bad convention)
        edges = [(j, i) for i in self.adj_n for j in self.adj_n[i]]
        self.G = gt.Graph(directed=True)
        self.G.add_edge_list(edges)
        vprop = self.G.new_vertex_property("string")
        for vertex in self.G.vertices():
            vertex_idx = self.G.vertex_index[vertex]
            vertex_name = self.int2node[vertex_idx]
            vprop[vertex] = vertex_name
        self.G.vertex_properties["name"] = vprop

    @property
    def pkg_paths(self) -> Iterator[Path]:
        return Path(self.path).glob("**/*.py")

    def get_adjacency_list(self) -> dict[str, set[str]]:
        module_set = ModuleSet([str(p) for p in self.pkg_paths])
        d = {m: module_set.mod_imports(m) for m in sorted(module_set.by_name)}
        return d

    def get_import_graph(self) -> dict[str, dict[str, set[str]]]:
        imports_in = self.get_adjacency_list()
        imports_out: dict[str, set[str]] = {}
        for module, imports in imports_in.items():
            for imported_name in imports:
                imports_out.setdefault(imported_name, set())
                imports_out[imported_name].add(module)
        graph = {
            module: {
                "in": imps_in,
                "out": imports_out.get(module, set()),
            }
            for module, imps_in in imports_in.items()
        }
        return graph

    @property
    def all_node_names(self):
        return sorted(
            {
                *self.adjacencies.keys(),
                *[val for adj in self.adjacencies.values() for val in adj],
            }
        )

    @property
    def int2node(self) -> dict[int, str]:
        return dict(enumerate(self.all_node_names))

    @property
    def node2int(self) -> dict[str, int]:
        return {n: i for i, n in self.int2node.items()}

    def numeric_adjacencies(self) -> dict[int, set[int]]:
        # Collect all module names from keys and values of adjacency list
        return {
            self.node2int[i]: set(self.node2int[j] for j in adj)
            for i, adj in self.adjacencies.items()
        }


def draw_directed_graph(path: str):
    mg = DirectedModuleGraph(path=path)
    graph_draw(mg.G, vertex_text=mg.G.vertex_properties["name"])
    return mg.get_import_graph()
