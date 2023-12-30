from __future__ import annotations

import json
import logging
from io import TextIOWrapper
from typing import Union

from .node import Edge, Node

logger = logging.getLogger(__name__)


class Topology:
    """
    Class for storing all the Nodes objects in the topology
    """

    log_prefix: str = __name__

    def __init__(self: Topology) -> None:
        self.nodes: dict[str, Node] = {}
        self.topology_file: str = ""

    def __str__(self: Topology) -> str:
        data: dict = {}
        for name in self.get_node_names():
            data[name] = self.nodes[name].to_dict()
        return json.dumps(data, indent=2)

    def add_node(self: Topology, node: Node) -> None:
        """
        Add a node to the topology

        :param Node node: Node object to add
        :rtype: None
        """
        if node not in self.get_nodes_list():
            self.nodes[node.get_name()] = node

    @staticmethod
    def from_dict(topo_data: dict[str, dict]) -> Topology:
        """
        Return a topology obj from a dict

        :param Dict topo_data: Dict of nodes and links
        :rtype: Topology
        """

        topology = Topology()

        """
        Load all the node objects
        """
        node_data: dict
        for node_data in topo_data["nodes"]:
            topology.add_node(Node.from_dict(node_data))

        """
        Load all the edge objects
        """
        edge_data: dict
        for edge_data in topo_data["links"]:
            edge: Edge = Edge.from_dict(topology.get_nodes(), edge_data)
            if edge.local not in topology.get_nodes_list():
                logger.error(
                    f"{Topology.log_prefix}: Can't add link from {edge.local} "
                    f"to {edge.remote}, {edge.local} is not in topology"
                )
            elif edge.remote not in topology.get_nodes_list():
                logger.error(
                    f"{Topology.log_prefix}: Can't add link from {edge.local} "
                    f"to {edge.remote}, {edge.remote} is not in topology"
                )
            edge.local.add_edge(edge)

        """
        Add any missing edges, to ensure they exist beween nodes in both
        directions
        """
        for node in topology.get_nodes_list():
            for neighbour in node.get_neighbours():
                if not node.edges_toward_node(neighbour):
                    for edge in neighbour.edges_toward_node(node):
                        new_edge = edge.copy()
                        new_edge.swap_nodes()
                        node.add_edge(new_edge)

        logger.info(
            f"{Topology.log_prefix}: Created topology with {topology.no_of_nodes()} "
            f"nodes and {topology.no_of_edges()} edges"
        )
        return topology

    @staticmethod
    def from_json(json_data: str) -> Topology:
        """
        Return a topology obj from a JSON string

        :param str json: JSON string to parse
        :rtype: Topology
        """
        topo_data: dict
        try:
            topo_data = json.loads(json_data)
        except Exception as e:
            logger.error(
                f"{Topology.log_prefix}: Couldn't parse topology string as "
                f"JSON: {json_data}"
            )
            raise e

        return Topology.from_dict(topo_data)

    @staticmethod
    def from_json_file(filename: str) -> Topology:
        """
        Return a topology obj from the contents of JSON file.

        :param str filename: JSON filename to load
        :rtype: Topology
        """
        json_file: TextIOWrapper
        json_data: str

        try:
            json_file = open(filename, "r")
            json_data = json_file.read()
        except Exception as e:
            logger.error(
                f"{Topology.log_prefix}: Couldn't open topology file {filename}"
            )
            raise e

        json_file.close()
        topology: Topology = Topology.from_json(json_data)
        topology.topology_file = filename
        return topology

    def get_node(self: Topology, node: str) -> Node:
        """
        Return the node object by name

        :param str node: Name of the node obj to return
        :raises ValueError: If the node doesn't exist in the topology
        :raises ValueError: If the node dict value is not set
        :rtype: Node
        """
        if node not in self.get_node_names():
            raise ValueError(f"Node {node} not found")
        if not self.nodes[node]:
            raise ValueError(f"Node is not defined")
        return self.nodes[node]

    def get_node_names(self: Topology) -> list[str]:
        """
        Return the list of node names in the topology

        :rtype: List
        """
        return list(self.nodes.keys())

    def get_nodes(self: Topology) -> dict[str, Node]:
        """
        Return a dict of all Node objects in this topology, keyed by node name

        :rtype: Dict
        """
        return self.nodes

    def get_nodes_list(self: Topology) -> list[Node]:
        """
        Return a list of all Node objects in this topology

        :rtype: List
        """
        return list(self.nodes.values())

    def no_of_edges(self: Topology) -> int:
        """
        Return the number of edges in the topology

        :rtype: int
        """
        count: int = 0
        for node in self.get_node_names():
            count += self.get_node(node).no_of_edges()
        return count

    def no_of_nodes(self: Topology) -> int:
        """
        Return the number of nodes in the topology

        :rtype: int
        """
        return len(self.get_nodes_list())

    def node_list_from_str(self: Topology, names: list[str]) -> list[Node]:
        """
        Return a list of nodes in the topology, given a list of node names

        :param List names: List of node names
        :rtype: List
        """
        return [self.get_node(name) for name in names]

    @staticmethod
    def to_dict(topology: Topology) -> dict[str, Union[bool, list]]:
        """
        Return a Topology obj serialised as a dict

        :param Topology topology: Topology to serialised to dict
        :rtype: Dict
        """
        nodes = []
        links = []
        for node in topology.get_nodes_list():
            nodes.append(node.to_dict(inc_edges=False))
            links += node.edges_to_list()

        topo_data: dict[str, Union[bool, list]] = {
            "directed": False,
            "multigraph": False,
            "nodes": nodes,
            "links": links,
        }

        logger.debug(
            f"{Topology.log_prefix}: Created dict with "
            f"{len(nodes)} nodes and "
            f"{len(links)} edges"
        )

        return topo_data

    @staticmethod
    def to_json(topology: Topology) -> str:
        """
        Return a JSON string serialisation of a topology

        :param Topology topology: Obj to serialise to JSON string
        :rtype: Topology
        """
        return json.dumps(Topology.to_dict(topology), indent=4)

    def to_json_file(
        self: Topology, filename: str, topology: Topology
    ) -> None:
        """
        Serialise a Topology to a file as a JSON string

        :param str Filename: Output filename path to write the JSON
        :param Topology topology: Topology object to serialise
        :rtype: None
        """
        json_data: str = Topology.to_json(topology)

        json_file: TextIOWrapper
        try:
            json_file = open(filename, "w")
            json_file.write(json_data)
        except Exception as e:
            logger.error(
                f"{Topology.log_prefix}: Couldn't write topology file "
                f"{filename}"
            )
            raise e

        json_file.close()
