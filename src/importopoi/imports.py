from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Import"]


@dataclass
class Import:
    from_name: str | None
    imported_name: str
    as_name: str | None
    relative_level: int | None

    @property
    def package_name(self) -> str | None:
        if self.relative_level and self.relative_level > 0:
            """
            >>> from .bar import foo  # Import("bar", "foo", None, 1)

            Note that relative imports without a module from_name
            are implicitly importing from an __init__.py

            >>> from . import foo  # Import(None, "foo", None, 1)
            >>> from .. import foo  # Import(None, "foo", None, 2)
            """
            package = None
        else:
            if self.from_name is None:
                """
                >>> import foo  # Import(None, "foo", None, 0)
                >>> import foo.bar  # Import(None, "foo.bar", None, 0)
                """
                package = self.imported_name.split(".")[0]
            else:
                """
                >>> from bar import foo  # Import("bar", "foo", None, 0)
                >>> from bar.baz import foo  # Import("bar.baz", "foo", None, 0)
                """
                package = self.from_name.split(".")[0]
        return package

    @property
    def module_qualname(self) -> str:
        """
        The qualname of the module that provides the imported name (not the imported
        name itself). May be relative.
        """
        qn = "." * self.relative_level if self.relative_level else ""
        if self.from_name is not None:
            qn += self.from_name
        return qn

    @property
    def qualname(self) -> str:
        """
        The qualname of the imported name. May be relative.
        """
        qn = self.module_qualname
        if self.from_name is None:
            """
            >>> import foo  # Import(None, "foo", None, 0)
            >>> import foo.bar  # Import(None, "foo.bar", None, 0)
            >>> from . import foo  # Import(None, "foo", None, 1)
            >>> from .. import foo  # Import(None, "foo", None, 2)
            """
            qn += self.imported_name
        else:
            """
            >>> from bar import foo  # Import("bar", "foo", None, 0)
            >>> from bar.baz import foo  # Import("bar.baz", "foo", None, 0)
            >>> from .bar import foo  # Import("bar", "foo", None, 1)
            """
            qn += "." + self.imported_name
        return qn

    def resolve_full_qualname(self, qual_path: str, module=True) -> str:
        """
        For a given module ``C`` at path ``A.B.C`` in the package ``A``, provide the
        full qualname (i.e. 'fully qualified' package-subpackage-module name) of the
        module a name is being imported from, by navigating up any relative levels,
        using the provided 'prefix', i.e.  the qualname of the module's parent directory
        (which here would be ``A.B``).

        A prefix is required for a relative import to be resolved to a qualname.

        If ``module`` is ``True`` (default), the qualname of the module which provides
        the imported name will be given rather than that of the imported name itself.
        If using the module's qualname, remember to check whether the qualname
        corresponds to a subpackage (and therefore implicitly an :mod:`__init__.py`
        module) or a module (named Python file).

        In the example below the module "A" must provide the name "D" from its
        :mod:`__init__.py` module, since "A" is the name of the subpackage with another
        subpackage "B" below it (which houses the module "C").

        >>> imp = Import(None, "D", None, 2) # from .. import D
        >>> assert imp.resolve_full_qualname(qual_path="A.B.C", module=True) == "A"
        >>> assert imp.resolve_full_qualname(qual_path="A.B.C", module=False) == "A.D"
        """
        if self.relative_level and self.relative_level > 0:
            if qual_path.startswith("."):
                raise ValueError(f"{qual_path=} must not be relative")
            if qual_path.count(".") < self.relative_level:
                raise ValueError(
                    f"{qual_path=} is too shallow for the relative level of the import "
                    f"({self.relative_level})",
                )
            qual_path_parts = qual_path.split(".")
            qual_prefix = ".".join(qual_path_parts[: -self.relative_level])
            rel_qn = self.module_qualname if module else self.qualname
            qualname = qual_prefix + "." + rel_qn.lstrip(".")
        else:
            qualname = self.module_qualname if module else self.qualname
        return qualname
