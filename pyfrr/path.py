from __future__ import annotations

from typing import List

from .node import Edge
from .topology import Topology


class Path:
    dst: str
    cost: int | None = None
    src: str
    path: List[Edge]

    def __init__(
        self,
        path: List[Edge],
        cost: int | None = None,
    ) -> None:

        self.path = path  ###### needs to be a list of edges
        self.source = path[0]  ###### Needs to be a node not an edge
        self.target = path[-1]  ###### Needs to be a node not an edge
        if cost:
            if type(cost) != int:
                raise ValueError(f"cost must be int not {type(cost)}")
            self.cost = cost

    @staticmethod
    def from_nx_list(path: List, topology: Topology) -> Path:
        return Path(path=[topology.nodes[node_name] for node_name in path])

    @staticmethod
    def from_nx_list_spf(cost: int, path: List, topology: Topology) -> Path:
        return Path(
            cost=cost, path=[topology.nodes[node_name] for node_name in path]
        )
