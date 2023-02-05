import logging
from typing import Dict, List

import networkx

from .path import EdgePath, EdgePaths, NodePath, NodePaths
from .topology import Topology


class AllPaths:
    topology: Topology
    paths: Dict[str, Dict[str, NodePaths]]  ###### type hinting mess !!!!

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
        Calculate all node paths and edge paths, between all nodes in the
        topology

        :rtype: None
        """
        self.paths = {}
        for src in self.topology.nodes:
            self.paths[src] = {}
            for dst in self.topology.nodes:
                if src == dst:
                    continue
                if src == "PE1" and dst == "PE5":
                    self.paths[src][dst] = self.get_node_paths(src, dst)
                    print(f"There are {len(self.paths[src][dst])} node paths")
                    for node_path in self.paths[src][dst]:
                        print(f"This node path is {len(node_path)} nodes long")
                        print(f"It has {node_path.no_edge_paths()} edge_paths")
                        for edge_path in node_path.edge_paths:
                            print(f"edge_path: {edge_path}")

        logging.info(f"Calculated {len(self)} {type(self)} paths")

    def get_node_paths(self, source: str, target: str) -> NodePaths:
        """
        Return all the node paths between source and target

        :param str source: Source node name in graph
        :param str target: Destination node name in graph
        :rtype: List
        """

        #  A NetworkX "simple path" is a path with no repeated nodes.
        node_paths: NodePaths = NodePaths()
        simple_path: List[str]
        all_simple_paths: List[List] = list(
            networkx.all_simple_paths(
                self.topology.graph, source=source, target=target
            )
        )

        logging.debug(
            f"{len(all_simple_paths)} simple paths between {source} and "
            f"{target}"
        )
        for simple_path in all_simple_paths:
            node_list: List = self.topology.node_list_from_str(simple_path)
            node_paths.add_node_path(NodePath(node_list))

        return node_paths

        """
        HOW TO ADD IN SRLGs? #############################################################################
        """
