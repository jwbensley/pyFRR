from __future__ import annotations

import json
import logging
from io import TextIOWrapper
from typing import Any, Dict, List

from .node import Edge, Node

logger = logging.getLogger(__name__)


class Topology:
    log_prefix: str = __name__
    nodes: Dict[str, Node]
    topology_file: str

    def __init__(self: Topology) -> None:
        self.nodes = {}
        self.topology_file = ""

    def __str__(self: Topology) -> str:
        data: Dict = {}
        for name in self.get_node_names():
            data[name] = self.nodes[name].to_dict()
        return json.dumps(data, indent=2)

    def add_node(self: Topology, node: Node) -> None:
        """
        Add a node to the topology

        :param Node node: Node object to add
        :rtype: None
        """
        if node.get_name() not in self.nodes:
            self.nodes[node.get_name()] = node

    @staticmethod
    def from_dict(topology: Dict[str, Any]) -> Topology:
        """
        Return a topology obj from a dict

        :param dict topology: dict of nodes and links
        :rtype: Topology
        """

        t = Topology()

        """
        Load all the node objects
        """
        n: Dict
        for n in topology["nodes"]:
            t.nodes[n["id"]] = Node.from_dict(n)

        """
        Load all the edge objects
        """
        e: Dict
        for e in topology["links"]:
            edge: Edge = Edge.from_dict(t.nodes, e)
            if edge.local.get_name() not in t.nodes:
                logger.error(
                    f"{Topology.log_prefix}: Can't add link from {edge.local} "
                    f"to {edge.remote}, {edge.local} is not in topology"
                )
            elif edge.remote.get_name() not in t.nodes:
                logger.error(
                    f"{Topology.log_prefix}: Can't add link from {edge.local} "
                    f"to {edge.remote}, {edge.remote} is not in topology"
                )
            t.nodes[edge.local.get_name()].add_edge(edge)

        """
        Add any missing edges which were only created in one direction
        """
        for node in t.get_nodes():
            for neighbour in node.get_neighbours():
                if not node.edges_toward_node(neighbour):
                    for edge in neighbour.edges_toward_node(node):
                        new_edge = edge.copy()
                        new_edge.swap_nodes()
                        node.add_edge(new_edge)

        logger.info(
            f"{Topology.log_prefix}: Created topology with {t.no_of_nodes()} "
            f"nodes and {t.no_of_edges()} edges"
        )
        return t

    @staticmethod
    def from_json(json_data: str) -> Topology:
        """
        Return a topology obj from a JSON string

        :param str json: JSON string to parse
        :rtype: Topology
        """
        topo_data: Dict
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
        t: Topology = Topology.from_json(json_data)
        t.topology_file = filename
        return t

    def get_node_by_name(self: Topology, name: str) -> Node:
        """
        Return the node object by name

        :param str name: Name of the node obj to return
        :rtype: Node
        """
        if name in self.nodes:
            return self.nodes[name]
        raise ValueError(f"Node {name} not found")

    def get_node_names(self: Topology) -> List[str]:
        """
        Return the list of node names in the topology

        :rtype: List
        """
        return list(self.nodes.keys())

    def get_nodes(self: Topology) -> List[Node]:
        """
        Return a list of all nodes in the topology

        :rtype: List
        """
        return list(self.nodes.values())

    def no_of_edges(self: Topology) -> int:
        """
        Return the number of edges in the topology

        :rtype: int
        """
        count: int = 0
        for node_name in self.nodes:
            count += self.nodes[node_name].no_of_edges()
        return count

    def no_of_nodes(self: Topology) -> int:
        """
        Return the number of nodes in the topology

        :rtype: int
        """
        return len(self.nodes)

    def node_list_from_str(self: Topology, node_path: List[str]) -> List[Node]:
        """
        Return a list of node in the topology, given a list of node names

        :param List node_path: List of node names
        :rtype: List
        """
        return [self.nodes[node] for node in node_path]

    @staticmethod
    def to_dict(t: Topology) -> Dict[str, Any]:
        """
        Return a JSON serialised dict of a topology, in NetworkX format

        :param Topology t: Topology to serialised to dict
        :rtype: dict
        """
        topo_data: Dict = {
            "directed": False,
            "multigraph": False,
            "nodes": [],
            "links": [],
        }

        for node in t.get_nodes():
            topo_data["nodes"].append(node.node_to_dict())
            topo_data["links"] += node.edges_to_list()

        logger.debug(
            f"{Topology.log_prefix}: Created dict with "
            f"{len(topo_data['nodes'])} nodes and "
            f"{len(topo_data['links'])} edges"
        )

        return topo_data

    @staticmethod
    def to_json(t: Topology) -> str:
        """
        Return a JSON string serialisation of a topology

        :param Topology t: Obj to serialise to JSON string
        :rtype: Topology
        """
        return json.dumps(Topology.to_dict(t), indent=4)

    def to_json_file(self: Topology, filename: str, t: Topology) -> None:
        """
        Serialise a Topology to a file as a JSON string

        :param str Filename: Output filename path to write the JSON
        :param Topology t: Topology object to serialise
        :rtype: None
        """
        json_data: str = Topology.to_json(t)

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
