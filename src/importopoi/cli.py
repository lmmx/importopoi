from argparse import ArgumentParser
import argcomplete

from .graph import draw_directed_graph
from .pprint_utils import pp


def run_cli():
    parser = ArgumentParser()
    parser.add_argument("src")
    argcomplete.autocomplete(parser)
    arg_l = parser.parse_args()
    graph_dict = draw_directed_graph(arg_l.src)
    pp(graph_dict)
