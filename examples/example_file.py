#!/usr/bin/env python3

import argparse
from typing import Dict
import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
)

from pypaths.pypaths import PyPaths
from pypaths.topology import Topology
from pypaths.settings import Settings


def parse_cli_args() -> Dict:
    parser = argparse.ArgumentParser(
        description="Parse graph topology data and generate paths between "
        "nodes in the graph",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--dev",
        help="Enable dev logging",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--json",
        help="Topology JSON file to parse",
        type=str,
        required=False,
        # default="examples/ecmp/ecmp.json",
        # default="examples/ring/ring.json",
        default="examples/mesh/mesh.json",
    )

    return vars(parser.parse_args())


def main():
    args: Dict = parse_cli_args()
    pp: PyPaths

    Settings.DEBUG = args["debug"]
    Settings.DEV = args["dev"]

    if args["json"]:
        pp = PyPaths(Topology.from_json_file(args["json"]))

    print(
        "All paths between PE1 and PE4:\n"
        f"{pp.all_paths.get_paths_between_by_name('PE1', 'PE4')}"
    )
    print(
        "Lowest weighted paths between PE1 and PE4:\n"
        f"{pp.spf_paths.get_paths_between_by_name('PE1', 'PE4')}"
    )
    print(
        "LFA paths between PE1 and PE4:\n"
        f"{pp.lfa_paths.get_paths_between_by_name('PE1', 'PE4')}"
    )

    for source in pp.topology.get_nodes():
        print(f"\"{source}\": {{")
        for target in pp.topology.get_nodes():
            if source == target:
                continue
            print(f"    \"{target}\": [")
            paths = pp.lfa_paths.get_paths_between(source, target)
            for path in paths:
                print(f"        {str(path).split(':')[1].strip()},")
            print(f"    ],")
        print("},")


main()
