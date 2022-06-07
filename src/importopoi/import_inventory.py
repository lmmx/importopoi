from __future__ import annotations

from pathlib import Path

from import_deps import ast_imports

from .imports import Import

__all__ = ["ModulePath", "ModuleImportsDict", "ImportInventory"]


"""
For simplicity coerce paths to strings to use as dict keys
"""
ModulePath = str
ModuleImportsDict = dict[ModulePath, list[Import]]


class ImportInventory:
    all_imports: ModuleImportsDict

    def __init__(self, files: list[Path | str]) -> None:
        self.all_imports = {
            ModulePath(module): [Import(*i) for i in ast_imports(module)]
            for module in files
        }

    @property
    def internal_imports(self) -> ModuleImportsDict:
        return {
            mod_path: (imps := [i for i in imports if i.relative_level > 0])
            for mod_path, imports in self.all_imports.items()
            # if imps  # uncomment to give only the modules which import the package
        }

    def package_imports(self, package_name: str) -> ModuleImportsDict:
        return {
            mod_path: (imps := [i for i in imports if i.package_name == package_name])
            for mod_path, imports in self.all_imports.items()
            # if imps  # uncomment to give only the modules which import the package
        }
