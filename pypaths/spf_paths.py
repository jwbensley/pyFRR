from __future__ import annotations

from .all_paths import AllPaths
from .path import Node
from .settings import Settings
from .topology import Topology


class SpfPaths(AllPaths):
    """
    Calculate only the equal cost lowest weighted paths between nodes in a
    topology
    """

    log_prefix: str = __name__

    def __init__(
        self: SpfPaths, all_paths: AllPaths, topology: Topology
    ) -> None:
        self.all_paths: AllPaths = all_paths
        self.topology: Topology = topology
        self.calculate_paths()

    def calculate_paths(self: SpfPaths) -> None:
        """
        Filter all_paths for the node paths and edge paths between all nodes in
        the topology, which are the lowest weighted paths

        :rtype: None
        """
        self._log(
            level=Settings.LOG_INFO,
            msg=f"Calculating all paths...",
        )

        self.paths = {}
        for source in self.topology.get_nodes_list():
            self.paths[source] = {}
            for target in self.topology.get_nodes_list():
                if source == target:
                    continue
                self.paths[source][target] = self.all_paths.get_paths_between(
                    source, target
                ).get_lowest_weighted_paths()

        self._log(
            level=Settings.LOG_INFO,
            msg=f"Calculated {len(self)} paths",
        )

    def get_path_cost_between(
        self: SpfPaths, source: Node, target: Node
    ) -> int:
        """
        Return the cost of the best path from a specific source to a specific
        target

        :param Node source: Source node in the topology
        :param Node target: Target node in the topology
        :rtype: int
        """
        if target not in self.paths[source]:
            raise ValueError(f"No paths between {source} and {target}")
        return self.paths[source][target].get_lowest_path_weight()
