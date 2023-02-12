import logging
from typing import Dict, List

from .node import Node
from .path import NodePath, NodePaths
from .topology import Topology


class AllPaths:
    topology: Topology
    paths: Dict[Node, Dict[Node, NodePaths]]

    def __init__(self, topology: Topology) -> None:
        self.topology = topology
        self.calculate_paths()

    def __len__(self) -> int:
        """
        Return the total number of simple paths that have been calculated in
        the topology.

        :rtype: int
        """
        count: int = 0
        for source in self.paths:
            for target in self.paths[source]:
                count += len(self.paths[source][target])
        return count

    def all_simple_paths(
        self,
        all_paths: NodePaths,
        current_path: List[Node],  ######## Should be a NodePath - FIXME
        source: Node,
        target: Node,
    ) -> NodePaths:
        """
        Return a NodePaths list of simple paths from source to target.
        This is a recursive depth first search, all_paths and current_path
        are not meant to be the passed in the initial call.

        :param NodePaths all_paths: Accruing list of all simple paths to target
        :param List current_path: The current path being searched
        :param Node source: Source node in the topology
        :param Node target: Target node in the topology
        :rtype: NodePaths
        """

        if current_path == []:
            current_path.append(source)

        for neighbour in [
            n
            for n in current_path[-1].get_neighbours()
            if n not in current_path
        ]:
            current_path.append(neighbour)

            if neighbour == target:
                all_paths.add_node_path(
                    NodePath(node_path=current_path.copy())
                )
                current_path.pop()
                continue

            self.all_simple_paths(all_paths, current_path, source, target)

        if len(current_path) > 1:
            current_path.pop()
        return all_paths

    def calculate_paths(self) -> None:
        """
        Calculate all node paths and edge paths, between all nodes in the
        topology

        :rtype: None
        """
        self.paths = {}
        for source in self.topology.get_node_names():
            self.paths[source] = {}
            for target in self.topology.get_node_names():
                if source == target:
                    continue
                self.paths[source][target] = self.all_simple_paths(
                    all_paths=NodePaths(node_paths=[]),
                    current_path=[],
                    source=self.topology.get_node_by_name(source),
                    target=self.topology.get_node_by_name(target),
                )

        logging.info(f"Calculated {len(self)} {type(self)} paths")
        """
        Stop the recursive edge adding when adding NodePath to NodePaths ################################

        HOW TO ADD IN SRLGs? #############################################################################
        """
