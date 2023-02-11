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
        self.calculate_all_paths()

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

    def calculate_all_paths(self) -> None:
        """
        Calculate all node paths and edge paths, between all nodes in the
        topology

        :rtype: None
        """
        self.paths = {}
        for source in self.topology.node_names():
            self.paths[source] = {}
            for target in self.topology.node_names():
                if source == target:
                    continue
                self.paths[source][target] = self.all_simple_paths(
                    all_paths=NodePaths(node_paths=[]),
                    current_path=[],
                    source=source,
                    target=target,
                )
                print(
                    f"There are {len(self.paths[source][target])} node paths between {source} and {target}"
                )
                print(
                    f"All paths from {source} to {target}: {self.paths[source][target]}"
                )
                for node_path in self.paths[source][target]:
                    print(f"This node path is {len(node_path)} nodes long")
                    print(f"It has {node_path.no_edge_paths()} edge_paths")
                    for edge_path in node_path.edge_paths:
                        print(f"edge_path: {edge_path}")

        logging.info(f"Calculated {len(self)} {type(self)} paths")

    def all_simple_paths(
        self,
        all_paths: NodePaths,
        current_path: List[Node],
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
            print(f"Initiallised current_path with {source}")

        if not current_path[-1].neighbours:
            print(f"Returning empty path")
            return NodePaths()

        print(
            f"{current_path[-1]} has neighbours {current_path[-1].neighbours}"
        )
        for neighbour in current_path[-1].neighbours:
            print(f"Current path is {current_path}, neighbour is {neighbour}")
            if neighbour not in current_path:
                current_path.append(neighbour)
                print(f"Added {neighbour} to current path")
                if neighbour == target:
                    print(f"Added new finished path: {current_path.copy()}")
                    all_paths.add_node_path(NodePath(current_path.copy()))
                    current_path.pop()
                    continue
                ret: List = self.all_simple_paths(
                    all_paths, current_path, source, target
                )
                if not ret:
                    all_paths.add_node_path(NodePath(current_path.copy()))
                    current_path.pop()
                else:
                    all_paths = ret

        if len(current_path) > 0:
            current_path.pop()
        return all_paths

        """
        Stop the recursive edge adding when adding NodePath to NodePaths ################################

        HOW TO ADD IN SRLGs? #############################################################################
        """
