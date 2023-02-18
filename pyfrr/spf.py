from __future__ import annotations

from typing import List

from .all_paths import AllPaths
from .path import NodePaths
from .settings import Settings


class Spf(AllPaths):
    def get_paths(self: Spf, source: str, target: str) -> List[NodePaths]:
        """
        Return all the shortest cost path(s) between source and target

        :param str source: Source node name in graph
        :param str target: Destination node name in graph
        :rtype: List
        """
        """
        nx_paths: List = []
        try:
            nx_paths = list(
                networkx.all_shortest_paths(
                    self.topology.graph,
                    source=source,
                    target=target,
                    weight=Settings.EDGE_WEIGHT,
                )
            )
        except networkx.exception.NetworkXNoPath:
            return []

        cost: int = networkx.shortest_path_length(
            self.topology.graph,
            source=source,
            target=target,
            weight=Settings.EDGE_WEIGHT,
        )
        paths: List = []
        shortest_path: List
        for shortest_path in nx_paths:
            paths.append(
                Path.from_nx_list_spf(
                    cost=cost, path=shortest_path, topology=self.topology
                )
            )
        return paths
        """
        return []

    def get_path_weight(self: Spf, path: List[NodePaths]) -> int:
        """
        Return the weight of an explicit path from source to target

        :param str source: Source node name in graph
        :param str target: Destination node name in graph
        :rtype: int
        """
        return 0

    def get_weight(self: Spf, source: str, target: str) -> int:
        """
        Return the weight of the shortest path from source to target

        :param str source: Source node name in graph
        :param str target: Destination node name in graph
        :rtype: int
        """
        """
        try:
            return networkx.shortest_path_length(
                self.topology.graph,
                source=source,
                target=target,
                weight=Settings.EDGE_WEIGHT,
            )
        except networkx.exception.NetworkXNoPath:
            return 0
        """
        return 0
