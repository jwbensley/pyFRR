from __future__ import annotations

import logging
from typing import Dict

from .node import Node
from .path import NodePath, NodePaths
from .topology import Topology

logger = logging.getLogger(__name__)


class AllPaths:
    """
    Calculate all paths between nodes in a topology
    """

    log_prefix: str = __name__

    class NoPathsFound(Exception):
        """
        No paths exists between source and target
        """

        def __init__(self: Exception, source: str, target: str):
            self.message: str = f"No paths exist between {source} and {target}"

        def __str__(self):
            return repr(self.message)

    def __init__(self: AllPaths, topology: Topology) -> None:
        self.paths: Dict[Node, Dict[Node, NodePaths]] = {}
        self.topology: Topology = topology
        self.calculate_paths()

    def __len__(self: AllPaths) -> int:
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

    def calculate_nodepaths(
        self: AllPaths,
        all_paths: NodePaths,
        current_path: NodePath,
        source: Node,
        target: Node,
    ) -> NodePaths:
        """
        Return a NodePaths list of simple paths from source to target.
        This is a recursive depth first search, all_paths and current_path
        are not meant to be the passed in the initial call.

        :param NodePaths all_paths: Accruing list of all simple paths to target
        :param NodePath current_path: The current path being searched
        :param Node source: Source node in the topology
        :param Node target: Target node in the topology
        :rtype: NodePaths
        """

        if not current_path:
            current_path.set_source(source)

        neighbour: Node
        for neighbour in [
            n
            for n in current_path[-1].get_neighbours()
            if n not in current_path
        ]:
            current_path.append(neighbour)

            if neighbour == target:
                all_paths.append(current_path.copy())
                current_path.pop()
                continue

            self.calculate_nodepaths(all_paths, current_path, source, target)

        if len(current_path) > 1:
            current_path.pop()
        return all_paths

    def calculate_paths(self: AllPaths) -> None:
        """
        Calculate all node paths and edge paths, between all nodes in the
        topology

        :rtype: None
        """
        self.paths = {}
        for source in self.topology.get_nodes():
            self.paths[source] = {}
            for target in self.topology.get_nodes():
                if source == target:
                    continue
                self.paths[source][target] = self.calculate_nodepaths(
                    all_paths=NodePaths(paths=[]),
                    current_path=NodePath(expand_edges=False, path=[]),
                    source=source,
                    target=target,
                )

        logger.info(f"{AllPaths.log_prefix}: Calculated {len(self)} paths")

    def get_paths_between(
        self: AllPaths, source: Node, target: Node
    ) -> NodePaths:
        """
        Return the NodePaths obj for node paths between the source and target

        :param Node source: Source of the NodePaths obj to return
        :param Node target: Target of the NodePaths obj to return
        :rtype: NodePaths
        """
        if target not in self.paths[source]:
            return NodePaths(paths=[])
        if not self.paths[source][target]:
            return NodePaths(paths=[])
        return self.paths[source][target]

    def get_paths_between_by_name(
        self: AllPaths, source: str, target: str
    ) -> NodePaths:
        """
        Return the NodePaths obj for node paths between the source and target

        :param str source: Source of the NodePaths obj to return
        :param str target: Target of the NodePaths obj to return
        :rtype: NodePaths
        """
        source_node: Node = self.topology.get_node_by_name(source)
        target_node: Node = self.topology.get_node_by_name(target)
        return self.get_paths_between(source_node, target_node)
