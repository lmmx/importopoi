from pathlib import Path
from typing import Iterator

import graph_tool as gt
from graph_tool.draw import graph_draw
from import_deps import ModuleSet

from .import_inventory import ImportInventory
from .log_utils import set_up_logging

__all__ = ["DirectedModuleGraph", "draw_directed_graph"]

logger = set_up_logging(__name__)


class DirectedModuleGraph:
    abbreviate_package_name = True
    "Remove the package name from qualnames (e.g. ``foo.bar`` --> ``.bar``"

    def __init__(self, path: str):
        self.path = path
        # Despite the name, the ModuleSet retains an order
        self.module_set: ModuleSet = ModuleSet([str(p) for p in self.pkg_paths])
        self.package_name = self.identify_package()
        self.adjacencies: dict[str, set[str]] = self.get_adjacency_list()
        self.import_inventory: ImportInventory = ImportInventory(files=self.pkg_paths)
        self.adj_n = self.numeric_adjacencies()
        """
        The 'adjacency list' is a list of imports, so reverse the edges,
        or else you'd represent "imports from" by an outbound edge (bad convention)
        """
        edges = [(j, i) for i in self.adj_n for j in self.adj_n[i]]
        self.G = gt.Graph(directed=True)
        self.G.add_edge_list(edges)
        self.set_node_names()
        self.set_edge_labels()

    def identify_package(self) -> str:
        if len(self.module_set.pkgs) != 1:
            # If there's one package with one part, the rest are subpackages
            root_pkgs = [p for p in self.module_set.pkgs if "." not in p]
            has_one_root_pkg = len(root_pkgs) == 1
            if has_one_root_pkg and all(
                pkg.startswith(root_pkgs[0]) for pkg in self.module_set.pkgs
            ):
                package = root_pkgs[0]
            else:
                raise ValueError(f"Expected one package in {self.module_set.pkgs=}")
        else:
            package = next(iter(self.module_set.pkgs))
        return package

    def set_node_names(self):
        """
        Create the 'name' vertex property from the node (i.e. package module) names.
        """
        vprop_name = self.G.new_vertex_property("string")
        for vertex in self.G.vertices():
            vertex_idx = self.G.vertex_index[vertex]
            vertex_name = self.int2nodename[vertex_idx]
            if self.abbreviate_package_name:
                vertex_name = vertex_name[vertex_name.find(".") :]
            vprop_name[vertex] = vertex_name
        self.G.vertex_properties["name"] = vprop_name

    def set_edge_labels(self):
        """
        Create the 'import_names' vertex property from the node (i.e. package module)
        import names.

        E.g. for this package, the edge from :mod:`.batch_multiprocessing` to
        :mod:`.conversion` should be labelled "batch_multiprocess, sequential_process"
        """
        eprop_edge_label = self.G.new_edge_property("string")
        edge_lookup = self.numeric_adjacencies()
        for vertex in self.G.vertices():
            "By convention, the file whose imports we read is the destination ('to')."
            vertex_to_idx = self.G.vertex_index[vertex]
            # breakpoint()
            # Iterate over the sources of imports to the current vertex
            for vertex_from_idx in edge_lookup[vertex_to_idx]:
                # if vertex_from_idx == 0:
                #    continue
                vertex_pair = (vertex_from_idx, vertex_to_idx)
                edge = self.G.edge(*vertex_pair)
                to_path = self.int2pkgpath[vertex_to_idx]
                to_qualname = self.int2nodename[
                    vertex_to_idx
                ]  # qualname: "pkgname.modname"
                from_qualname = self.int2nodename[vertex_from_idx]
                to_imports = self.import_inventory.all_imports[str(to_path)]
                # to_imported_qualnames = {
                #     i.resolve_full_qualname(qual_path=to_qualname, module=True)
                #     for i in to_imports
                #     if i.package_name in (None, self.package_name)
                # }
                to_imported_names = {
                    i.imported_name
                    for i in to_imports
                    if i.package_name in (None, self.package_name)
                    if from_qualname
                    == i.resolve_full_qualname(qual_path=to_qualname, module=True)
                }
                imported_names_label = ", ".join(to_imported_names)
                # if vertex_from_idx > 0:
                #     breakpoint()
                # edge_label = ", ".join(imported_names)
                # vertex_edge_label = self.intpair2edgelabel[edge_idx_pair]
                # eprop_edge_label[edge] = f"{vertex_pair}" # vertex_edge_label
                eprop_edge_label[edge] = imported_names_label
        self.G.edge_properties["edge_label"] = eprop_edge_label

    @property
    def pkg_paths(self) -> Iterator[Path]:
        return Path(self.path).glob("**/*.py")

    def get_adjacency_list(self) -> dict[str, set[str]]:
        d = {m: self.module_set.mod_imports(m) for m in self.module_set.by_name}
        return d

    def get_import_graph(self) -> dict[str, dict[str, set[str]]]:
        imports_in = self.adjacencies
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

    # @property
    # def all_node_names(self):
    #    return sorted(
    #        {
    #            *self.module_set.by_name, # Also the keys of self.adjacencies
    #            *[val for adj in self.adjacencies.values() for val in adj],
    #        }
    #    )

    @property
    def int2nodename(self) -> dict[int, str]:
        return dict(enumerate(self.module_set.by_name))

    @property
    def int2pkgpath(self) -> dict[int, Path]:
        return dict(enumerate(self.pkg_paths))

    @property
    def node2int(self) -> dict[str, int]:
        return {n: i for i, n in self.int2nodename.items()}

    def numeric_adjacencies(self) -> dict[int, set[int]]:
        """Collect all module names from keys and values of adjacency list"""
        return {
            self.node2int[i]: set(self.node2int[j] for j in adj)
            for i, adj in self.adjacencies.items()
        }

    def draw(self) -> None:
        graph_draw(
            self.G,
            vertex_text=self.G.vertex_properties["name"],
            vertex_font_size=20,
            edge_text=self.G.edge_properties["edge_label"],
            edge_font_size=20,
            edge_text_distance=20,
        )


def draw_directed_graph(path: str):
    mg = DirectedModuleGraph(path=path)
    import_graph = mg.get_import_graph()
    mg.draw()
    return import_graph
