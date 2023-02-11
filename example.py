#!/usr/bin/env python3

import argparse
from typing import Dict
import sys
from pyfrr.pyfrr import PyFrr


def parse_cli_args() -> Dict:

    parser = argparse.ArgumentParser(
        description="Parse graph topology data and calculate paths between "
        "nodes in the graph",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        "-d",
        help="Enable debug logging",
        default=False,
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--topology",
        "-t",
        help="Topology file to parse",
        type=str,
        required=False,
        default="pyfrr/tests/ecmp1.json",
        #default="pyfrr/tests/test_topology.json",
        #default="old/example/ring.json",
    )

    return vars(parser.parse_args())


def main():
    args: Dict = parse_cli_args()

    p: PyFrr = PyFrr()
    p.load_nx_json(args["topology"])

    sys.exit(0)


main()
