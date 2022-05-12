from pprint import pprint

__all__ = ["pp"]

pp = lambda x: pprint(x, sort_dicts=False)
