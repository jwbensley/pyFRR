from __future__ import annotations

import logging
from typing import Dict, List

from .all_paths import AllPaths
from .node import Node
from .path import NodePath, NodePaths
from .settings import Settings
from .topology import Topology


class Spf(AllPaths):
    def __init__(self: Spf, all_paths: AllPaths, topology: Topology) -> None:
        self.all_paths: AllPaths = all_paths
        self.paths: Dict[Node, Dict[Node, NodePaths]] = {}
        self.topology: Topology = topology
        self.calculate_paths()

    def __len__(self: Spf) -> int:
        """
        Return the total number of lowest weight paths that have been found in
        the topology.

        :rtype: int
        """
        count: int = 0
        for source in self.paths:
            for target in self.paths[source]:
                count += len(self.paths[source][target])
        return count

    def calculate_paths(self: Spf) -> None:
        """
        Filter all_paths for the node paths and edge paths between all nodes in
        the topology, which are the shortest weighted paths

        :rtype: None
        """
        self.paths = {}
        for source in self.topology.get_nodes():
            self.paths[source] = {}
            for target in self.topology.get_nodes():
                if source == target:
                    continue
                self.paths[source][target] = self.all_paths.get_paths_between(
                    source, target
                ).get_lowest_weight_nodepaths()

        logging.info(f"Calculated {len(self)} {type(self)} paths")
