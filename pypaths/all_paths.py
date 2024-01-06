from __future__ import annotations

import logging

from .node import Node
from .path import NodePath, NodePaths
from .settings import Settings
from .topology import Topology

logger = logging.getLogger(__name__)


class AllPaths:
    """
    This is the base class for all path groups.

    Calculate all paths between nodes in a topology.
    """

    log_prefix: str = __name__

    class NoPathsFound(Exception):
        """No paths exists between source and target."""

        def __init__(self: AllPaths.NoPathsFound, source: str, target: str):
            self.message: str = f"No paths exist between {source} and {target}"

        def __str__(self: AllPaths.NoPathsFound) -> str:
            return repr(self.message)

    def __init__(self: AllPaths, topology: Topology) -> None:
        self.paths: dict[Node, dict[Node, NodePaths]] = {}
        self.topology: Topology = topology
        self.calculate_paths()

    def __len__(self: AllPaths) -> int:
        """
        Return the total number of simple paths that have been calculated in
        the topology.

        :rtype: int
        """
        count: int = 0
        for source in self.get_sources():
            paths_from_source = self.get_paths_from(source)
            for target in paths_from_source:
                count += len(paths_from_source[target])
        return count

    def _log(self: AllPaths, level: str, msg: str) -> None:
        """
        Issue a log message with this classes specific log prefix
        """
        match level:
            case Settings.LOG_INFO:
                logger.info(f"{self.log_prefix}: {msg}")
            case Settings.LOG_DEBUG:
                logger.debug(f"{self.log_prefix}: {msg}")
            case Settings.LOG_DEV:
                logger.log(
                    level=Settings.LOG_DEV_LEVEL,
                    msg=f"{self.log_prefix}: {msg}",
                )

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

        penultimate_node: Node = current_path[-1]
        for neighbour in penultimate_node.get_neighbours():
            if neighbour in current_path:
                continue

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
        topology.

        :rtype: None
        """

        self._log(level=Settings.LOG_INFO, msg="Calculating all paths...")

        self.delete_paths()
        for source in self.topology.get_nodes_list():
            for target in self.topology.get_nodes_list():
                if source == target:
                    continue
                self.set_path(
                    paths=self.calculate_nodepaths(
                        all_paths=NodePaths(paths=[]),
                        current_path=NodePath(expand_edges=False, path=[]),
                        source=source,
                        target=target,
                    ),
                    source=source,
                    target=target,
                )

        self._log(level=Settings.LOG_INFO, msg=f"Calculated {len(self)} paths")

    def delete_paths(self: AllPaths) -> None:
        """
        Delete all paths.

        :rtype: None
        """
        self.paths = {}
        self._log(level=Settings.LOG_DEBUG, msg="Deleted all paths")

    def get_paths_between(
        self: AllPaths, source: Node, target: Node
    ) -> NodePaths:
        """
        Return the NodePaths obj for node paths between the source and target.

        :param Node source: Source of the NodePaths obj to return
        :param Node target: Target of the NodePaths obj to return
        :rtype: NodePaths
        """
        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Getting all paths between {source} and {target}",
        )

        if source not in self.get_sources():
            return NodePaths(paths=[])

        paths_from_source = self.get_paths_from(source)
        if target not in paths_from_source:
            return NodePaths(paths=[])
        return paths_from_source[target]

    def get_paths_between_by_name(
        self: AllPaths, source: str, target: str
    ) -> NodePaths:
        """
        Return the NodePaths obj for node paths between the source and target.

        :param str source: Source of the NodePaths obj to return
        :param str target: Target of the NodePaths obj to return
        :rtype: NodePaths
        """
        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Getting all paths between {source} and {target}",
        )

        source_node: Node = self.topology.get_node(source)
        target_node: Node = self.topology.get_node(target)
        return self.get_paths_between(source_node, target_node)

    def get_paths_from(self: AllPaths, source: Node) -> dict[Node, NodePaths]:
        """
        Get all NodePaths from a specific source keyed by target node name.

        :param Node source: Source node to return NodePaths for
        :rtype: dict
        """
        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Getting all paths from {source}",
        )

        if source not in self.get_sources():
            return {}
        return self.paths[source]

    def get_sources(self: AllPaths) -> list[Node]:
        """
        Get the list of source nodes which have paths calculated.

        :rtype: list
        """

        return list(self.paths.keys())

    def set_path(
        self: AllPaths, paths: NodePaths, source: Node, target: Node
    ) -> None:
        """
        Set the paths between a source and target.

        :param NodePaths paths: NodePaths obj to set
        :param Node source: Source of the NodePaths obj
        :param Node target: Destination of the NodePaths obj
        :rtype: None
        """

        if source not in self.get_sources():
            self.paths[source] = {}
        self.paths[source][target] = paths
