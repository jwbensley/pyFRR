#!/usr/bin/env python3

import argparse
from typing import Dict
import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
)

from pyfrr.pyfrr import PyFrr
from pyfrr.settings import Settings

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
        #default="examples/ecmp/ecmp.json",
        # default="examples/ring/ring.json",
        default="examples/mesh/mesh.json",
    )

    return vars(parser.parse_args())


def main():
    args: Dict = parse_cli_args()

    if args["debug"]:
        Settings.DEBUG = True

    p: PyFrr = PyFrr(args["topology"])

    sys.exit(0)


main()
