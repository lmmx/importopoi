from __future__ import annotations

from pprint import pprint

__all__ = ["pp"]


def pp(x) -> None:
    pprint(x, sort_dicts=False)
