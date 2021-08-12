#!/usr/bin/env python3

# Example script to show how to use the pyFRR module API.

# Requires: pip3 install argparse
import argparse
import pprint
import sys
sys.path.append('./')
from pyfrr import pyfrr


# Example topology
links = [
    {"source": "P1", "target": "P2", "weight": 10},
    {"source": "P2", "target": "P4", "weight": 10},
    {"source": "P3", "target": "P4", "weight": 10},
    {"source": "P3", "target": "P1", "weight": 10},
    {"source": "P1", "target": "P5", "weight": 1},
    {"source": "P5", "target": "PE1", "weight": 1},
    {"source": "PE1", "target": "P2", "weight": 10},
    {"source": "PE2", "target": "P3", "weight": 10},
    {"source": "PE2", "target": "P4", "weight": 10},
    {"source": "PE3", "target": "P1", "weight": 10},
    {"source": "PE3", "target": "P3", "weight": 10},
    {"source": "PE4", "target": "P2", "weight": 10},
    {"source": "PE4", "target": "P4", "weight": 10},
    {"source": "PE5", "target": "P2", "weight": 10},
    {"source": "PE5", "target": "P4", "weight": 10},
]
nodes = [
    {"id": "P1"},
    {"id": "P2"},
    {"id": "P3"},
    {"id": "P4"},
    {"id": "PE1"},
    {"id": "PE2"},
    {"id": "PE3"},
    {"id": "PE4"},
    {"id": "PE5"},
    {"id": "P5"},
]

pp = pprint.PrettyPrinter(indent=2)


def parse_cli_args():

    parser = argparse.ArgumentParser(
        description="Read topology data from a JSON file, calculate FRR "
        "paths and generate diagrams of the backup paths.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--base",
        help="Use with --diagram to rende a diagram of the base topology (no highlighted paths).",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--debug",
        help="Set debug level: 0, 1 or 2.",
        type=int,
        default=0,
        required=False,
    )
    parser.add_argument(
        "--diagram",
        help="Render diagrams of the calculated paths.",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--diagram-all",
        help="Render diagrams for all path types.",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--lfa",
        help="Calculate the LFA paths between each node in the graph.",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--rlfa",
        help="Calculate the rLFA paths between each node in the graph.",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--print",
        help="Print the calculated paths to the screen.",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--spf",
        help="Calculate shortest paths between each node in the graph.",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--tilfa",
        help="Calculate the TI-LFA paths between each node in the graph.",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--topology",
        help="Topology data file to load.",
        type=str,
        required=False,
        default=None,
    )
    parser.add_argument(
        "--type",
        help="Topology data file type.",
        type=str,
        required=False,
        default=None,
    )

    return vars(parser.parse_args())


def pprint_base(f):
    """
    Print the base topology data.
    """

    pp.pprint(f.graph_to_json())


def pprint_lfas(f):
    """
    Print all the calculated LFA paths.
    """

    for src, dst in [(s, d) for d in f.topo for s in f.topo if s != d]:
        for path_type in f.lfa.path_types:
            if path_type in f.topo[src][dst]:
                print(f"{path_type} path(s) from {src} to {dst}: ", end="")
                if f.topo[src][dst][path_type]:
                    print(f.topo[src][dst][path_type])
                else:
                    print(f.topo[src][dst][path_type])


def pprint_rlfas(f):
    """
    Print all the calculated rLFA paths.
    """

    for src, dst in [(s, d) for d in f.topo for s in f.topo if s != d]:
        for path_type in f.rlfa.path_types:
            if path_type in f.topo[src][dst]:
                print(f"{path_type} path(s) from {src} to {dst}: ", end="")
                paths = []
                for path in f.topo[src][dst][path_type]:
                    for s_p_path in path[0]:
                        for p_d_path in path[1]:
                            paths.append(s_p_path + p_d_path[1:])
                print(paths)


def pprint_spf(f):
    """
    Print all the calculated shortest paths.
    """

    for src, dst in [(s, d) for d in f.topo for s in f.topo if s != d]:
        for path_type in f.spf.path_types:
            if path_type in f.topo[src][dst]:
                print(f"{path_type} path(s) from {src} to {dst}: ", end="")
                print(f.topo[src][dst][path_type])


def pprint_tilfas(f):
    """
    Print all the calculated TI-LFA paths.
    """
    """
    for src, dst in [(s, d) for d in f.topo for s in f.topo if s != d]:
        for path_type in f.tilfa.path_types:
            if path_type in f.topo[src][dst]:
                print(f"{path_type} path(s) from {src} to {dst}: ", end="")
                paths = []
                for path in f.topo[src][dst][path_type]:
                    for s_p_path in path[0]:
                        for p_d_path in path[1]:
                            paths.append(s_p_path + p_d_path[1:])
                print(paths)
    """
    ##################################################### TODO

def main():

    args = parse_cli_args()

    # Example module usage with a topology JSON file:
    if args["topology"]:
        f = pyfrr(
            filename=args["topology"],
            filetype=args["type"],
            debug=args["debug"]
        )

        if not f:
            print("Failed to initial pyFRR module")
            return

        if args["base"]:
            if args["diagram"]:
                outdir = f.draw_base()
                if outdir:
                    print(f"Rendered base topology diagram to {outdir}")
            if args["print"]:
                pprint_base(f)

        if args["spf"]:
            f.gen_all_metric_spfs()
            if args["diagram"]:
                outdir = f.draw_spf()
                if outdir:
                    print(f"Rendered shortest path diagrams to {outdir}")
            if args["print"]:
                pprint_spf(f)

        if args["lfa"]:
            f.gen_all_metric_lfas()
            if args["diagram"]:
                outdir = f.draw_lfas()
                if outdir:
                    print(f"Rendered LFA path diagrams to {outdir}")
            if args["print"]:
                pprint_lfas(f)

        if args["rlfa"]:
            f.gen_all_metric_rlfas()
            if args["diagram"]:
                outdir = f.draw_rlfas()
                if outdir:
                    print(f"Rendered rLFA path diagrams to {outdir}")
            if args["print"]:
                pprint_rlfas(f)

        if args["tilfa"]:
            f.gen_all_metric_tilfas()
            if args["diagram"]:
                outdir = f.draw_tilfas()
                if outdir:
                    print(f"Rendered TI-LFA path diagrams to {outdir}")
            if args["print"]:
                pprint_tilfas(f)

        # Use f.draw() to render multiple diagram types
        if args["diagram_all"]:
            f.gen_all_metric_spfs()
            f.gen_all_metric_lfas()
            f.gen_all_metric_rlfas()
            f.gen_all_metric_tilfas()
            outdir = f.draw(None, ["base", "spf", "lfa", "rlfa", "tilfa"])
            if outdir:
                print(f"All diagrams rendered to {outdir}")

    # Example module usage with nodes+links dicts
    else:
        print(f"No topology file passed, using example topology")
        f = pyfrr(links=links, nodes=nodes, debug=args["debug"])

        if not f:
            print("Failed to initial pyFRR module")
            return

        """
        f.gen_all_metric_spfs()
        f.gen_all_metric_lfas()
        f.gen_all_metric_rlfas()

        print("All paths from PE1 to PE2:")
        pp.pprint(f.get_paths(src="PE1", dst="PE2"))
        print("All paths from PE2 to PE1:")
        pp.pprint(f.get_paths(src="PE2", dst="PE1"))
        print("All paths from PE1:")
        pp.pprint(f.get_paths(src="PE1"))
        print("All paths to PE2:")
        pp.pprint(f.get_paths(dst="PE2"))

        print("All paths via PE1:")
        pp.pprint(f.get_paths_via(via="PE1"))

        outdir = f.draw_spf("./example_topo_spf_diagrams")
        if outdir:
            print(f"Rendered shortest path diagrams to {outdir}")
        """

        f.gen_all_metric_tilfas()

    sys.exit()

main()
