import json
import logging
from io import TextIOWrapper
from typing import Dict, List
from .node import Edge, Node


class Topology:
    nodes: Dict[str, Node]
    topology_file: str

    def __init__(self) -> None:
        self.nodes = {}

    def __str__(self) -> str:
        data: Dict = {}
        for node in self.nodes:
            data[node.name] = self.nodes[node].to_dict()
        return json.dumps(data, indent=2)

    def add_node(self, node: Node) -> None:
        """
        Add a node to the topology

        :param Node node: Node object to add
        :rtype: None
        """
        if node.name not in self.nodes:
            self.nodes[node.name] = node

    def edge_from_nx_edge(self, nx_edge: Dict) -> Edge:
        """
        Return an Edge obj from an NX formatted dict
        :param Dict nx_edge: An NX syntax link object
        :rtype: Edge
        """
        return Edge(
            local=self.nodes[nx_edge["source"]],
            remote=self.nodes[nx_edge["target"]],
            adj_sid=nx_edge["adj_sid"] if "adj_sid" in nx_edge else None,
            weight=nx_edge["weight"] if "weight" in nx_edge else None,
        )

    def from_nx_dict(self, topology: Dict) -> None:
        """
        Create the topology from a NX syntax dictionary

        :param dict topology: NetworkX formatted dict of nodes and links
        :rtype: None
        """

        """
        Erase the existing topology
        """
        self.topology_file = ""
        self.nodes = {}

        nx_node: Dict
        for nx_node in topology["nodes"]:
            self.nodes[nx_node["id"]] = self.node_from_nx_node(nx_node)

        nx_edge: Dict
        for nx_edge in topology["links"]:
            edge = self.edge_from_nx_edge(nx_edge)
            if edge.local.name not in self.nodes:
                logging.error(
                    f"Can't add link from {edge.local} to {edge.remote}, "
                    f"{edge.local} is not in topology"
                )
            elif edge.remote.name not in self.nodes:
                logging.error(
                    f"Can't add link from {edge.local} to {edge.remote}, "
                    f"{edge.remote} is not in topology"
                )
            self.nodes[edge.local.name].add_edge(edge)

        logging.debug(
            f"Created topology with {self.no_of_nodes()} nodes and "
            f"{self.no_of_edges()} edges"
        )

    def from_nx_json(self, json_data: str) -> None:
        """
        Build the topology data from a JSON string

        :param str json: JSON string to parse
        :rtype: None
        """
        topo_data: Dict
        try:
            topo_data = json.loads(json_data)
        except Exception as e:
            logging.error(
                f"Couldn't parse topology string as JSON: {json_data}"
            )
            raise e

        self.from_nx_dict(topo_data)

    def from_nx_json_file(self, filename: str) -> None:
        """
        Build the topology data from the contents of JSON file.

        :param str filename: JSON filename to load
        :rtype: None
        """
        json_file: TextIOWrapper
        json_data: str

        try:
            json_file = open(filename, "r")
            json_data = json_file.read()
        except Exception as e:
            logging.error(f"Couldn't open topology file {filename}")
            raise e

        json_file.close()
        self.from_nx_json(json_data)
        self.topology_file = filename

    def get_node_by_name(self, name: str) -> Node:
        """
        Return the node object by name

        :param str name: Name of the node obj to return
        :rtype: Node
        """
        if name in self.nodes:
            return self.nodes[name]
        raise ValueError(f"Node {name} not found")

    def no_of_edges(self) -> int:
        """
        Return the number of edges in the topology

        :rtype: int
        """
        count: int = 0
        for node_name in self.nodes:
            count += self.nodes[node_name].no_of_edges()
        return count

    def no_of_nodes(self) -> int:
        """
        Return the number of nodes in the topology

        :rtype: int
        """
        return len(self.nodes)

    def node_from_nx_node(self, nx_node: Dict) -> Node:
        """
        Return a new Node obj from a dict using networkx syntax

        :param Dict nx_node: Node obj serialised as dict in networkx format
        :rtype: Node
        """
        return Node(
            edges={},
            name=nx_node["id"],
            neighbours=[],
            node_sid=nx_node["node_sid"] if "node_sid" in nx_node else None,
        )

    def node_list_from_str(self, node_path: List[str]) -> List[Node]:
        """
        Return a list of node obj's given a list of node names

        :param List node_path: List of node names
        :rtype: List
        """
        return [self.nodes[node] for node in node_path]

    def node_names(self) -> List[str]:
        """
        Return the list of node names in the topology

        :rtype: List
        """
        return self.nodes.values()

    def to_dict(self) -> Dict:
        """
        Return a JSON serializable dict for the topo data, inc NetworkX attrs

        :rtype: dict
        """
        topo_data: Dict = {
            "directed": False,
            "multigraph": False,
            "nodes": [],
            "links": [],
        }

        for node_name in self.nodes:
            topo_data["nodes"].append(self.nodes[node_name].node_to_dict())
            topo_data["links"].append(self.nodes[node_name].edges_to_list())

        logging.debug(
            f"Created dict with {len(topo_data['nodes'])} nodes and "
            f"{len(topo_data['links'])} edges"
        )

        return topo_data
