import json
import logging
from io import TextIOWrapper
from typing import Dict, List

import networkx

from .node import Node


class Topology:
    directed: bool
    graph: networkx.Graph
    nodes: Dict[str, Node]
    multigraph: bool
    topology_file: str

    def __init__(self) -> None:
        self.graph = networkx.Graph()
        self.nodes = {}

    def __str__(self) -> str:
        data: Dict = {}
        for node in self.nodes:
            data[node] = self.nodes[node].to_dict()
        return json.dumps(data, indent=2)

    def add_node(self, node: Node) -> None:
        """
        Add a node to the topology

        :param Node node: Node object to add
        :rtype: None
        """
        if node.name not in self.nodes:
            self.nodes[node.name] = node
        else:
            raise ValueError(f"Node {node.name} already exists in topology")

    def create_graph(self) -> None:
        """
        Create the node/edge graph from stored topology data

        :rtype: None
        """
        if not self.nodes:
            raise ValueError(f"No topology data to create graph from")

        try:
            self.graph = networkx.readwrite.json_graph.node_link_graph(
                self.to_dict()
            )
        except Exception as e:
            print("Couldn't convert topology JSON data to NetworkX graph")
            raise e

        logging.debug(
            f"Created graph with {len(self.graph.nodes)} nodes and "
            f"{len(self.graph.edges)} edges"
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
        self.graph = networkx.Graph

        """
        Add in the fields required by NetworkX.
        """
        if "directed" in topology:
            self.directed = topology["directed"]
        else:
            self.directed = False
        if "multigraph" in topology:
            self.multigraph = topology["multigraph"]
        else:
            self.multigraph = False

        node: Dict
        for node in topology["nodes"]:
            if node["id"] not in self.nodes:
                self.nodes[node["id"]] = Node.from_nx_dict(node)
                self.nodes[node["id"]].add_edges_from_nx_dict(
                    topology["links"]
                )

        logging.debug(
            f"Created topology with {self.no_of_nodes()} nodes and "
            f"{self.no_of_edges()} edges"
        )

        self.create_graph()

    def from_nx_json(self, json_data: str) -> None:
        """
        Build the topology data and graph from a JSON string

        :param str json: JSON string to parse
        :rtype: None
        """
        topo_data: Dict
        try:
            topo_data = json.loads(json_data)
        except Exception as e:
            print(f"Couldn't parse topology string as JSON: {json_data}")
            raise e

        self.from_nx_dict(topo_data)

    def from_nx_json_file(self, filename: str) -> None:
        """
        Build the topology data and graph from the contents of JSON file.

        :param str filename: JSON filename to load
        :rtype: None
        """
        json_file: TextIOWrapper
        json_data: str

        try:
            json_file = open(filename, "r")
            json_data = json_file.read()
        except Exception as e:
            print(f"Couldn't open topology file {filename}")
            raise e

        json_file.close()
        self.from_nx_json(json_data)
        self.topology_file = filename

    def no_of_edges(self) -> int:
        """
        Return the number of edges in the topology

        :rtype: int
        """
        count: int = 0
        for node in self.nodes:
            count += self.nodes[node].no_of_edges()
        return count

    def no_of_nodes(self) -> int:
        """
        Return the number of nodes in the topology

        :rtype: int
        """
        return len(self.nodes)

    def node_list_from_str(self, node_path: List[str]) -> List[Node]:
        """
        Return a list of node obj's given a list of node names

        :param List node_path: List of node names
        :rtype: List
        """
        return [self.nodes[node] for node in node_path]

    def to_dict(self) -> Dict:
        """
        Return a JSON serializable dict for the topo data, inc NetworkX attrs

        :rtype: dict
        """
        topo_data: Dict = {
            "directed": self.directed,
            "multigraph": self.multigraph,
            "nodes": [],
            "links": [],
        }

        for node in self.nodes:
            topo_data["nodes"].append(self.nodes[node].node_to_dict())
            topo_data["links"] += self.nodes[node].edges_to_list()

        logging.debug(
            f"Created dict with {len(topo_data['nodes'])} nodes and "
            f"{len(topo_data['links'])} edges"
        )

        return topo_data
