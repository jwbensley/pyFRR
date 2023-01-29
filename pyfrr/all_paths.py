import logging
from typing import Dict, List

import networkx

from .path import Path
from .topology import Topology


class AllPaths:
    topology: Topology
    # paths = {"source": {"target": [ path1, path2 ] } }
    paths: Dict[str, Dict[str, List[Path]]] = {}

    def __init__(self, topology: Topology) -> None:
        self.topology = topology
        self.calculate_all_paths()

    def __len__(self) -> int:
        """
        Return the total number of simple paths that have been calculated in
        the topology.

        :rtype: int
        """
        count: int = 0
        for src in self.paths:
            for dst in self.paths[src]:
                count += len(self.paths[src][dst])
        return count

    def calculate_all_paths(self) -> None:
        """
        Calculate all paths between all nodes in the topology

        :rtype: None
        """
        for src in self.topology.nodes:
            if src not in self.paths:
                self.paths[src] = {}
            for dst in self.topology.nodes:
                if src == dst:
                    continue
                if dst not in self.paths[src]:
                    self.paths[src][dst] = self.get_paths(src, dst)

        logging.debug(f"Calculated {len(self)} {type(self)} paths")

    def get_paths(self, source: str, target: str) -> List[Path]:
        """
        Return all the paths between source and target

        :param str source: Source node name in graph
        :param str target: Destination node name in graph
        :rtype: List
        """

        # A simple path is a path with no repeated nodes.
        paths: List = []
        simple_path: List
        for simple_path in networkx.all_simple_paths(
            self.topology.graph, source=source, target=target
        ):
            paths.append(Path.from_nx_list(simple_path, self.topology))

        return paths

        """
        HOW TO ADD IN SRLGs? #############################################################################
        """
