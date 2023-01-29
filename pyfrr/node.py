from __future__ import annotations

from typing import Dict, List


class Edge:
    local: Node
    remote: Node
    adj_sid: int | None = None
    weight: int | None = None

    def __init__(
        self,
        local: Node,
        remote: Node,
        adj_sid: int | None = None,
        weight: int | None = None,
    ) -> None:
        if not local or not remote:
            raise ValueError("local and remote must be defined")

        self.local = local
        self.remote = remote

        if adj_sid:
            if type(adj_sid) != int:
                raise ValueError(f"adj_sid must be int not {type(adj_sid)}")
            self.adj_sid = adj_sid

        if weight:
            if type(weight) != int:
                raise ValueError(f"weight must be int not {type(weight)}")
            self.weight = weight

    def to_dict(self) -> Dict:
        """
        Return a JSON serializable dict of the Edge
        """
        return {
            "source": str(self.local),
            "target": str(self.remote),
            "adj_sid": self.adj_sid,
            "weight": self.weight,
        }

    @staticmethod
    def from_nx_dict(edge: Dict) -> Edge:
        """
        Return a new Edge obj from a dict using networkx syntax

        :param Dict edge: Edge obj serialised as dict in networkx format
        :rtype: Edge
        """
        new_edge: Edge = Edge(local=edge["source"], remote=edge["target"])
        if "adj_sid" in edge:
            new_edge.adj_sid = edge["adj_sid"]
        if "weight" in edge:
            new_edge.weight = edge["weight"]
        return new_edge


class Node:
    edges: Dict[str, List[Edge]] = {}
    name: str
    node_sid: int | None = None

    def __init__(
        self,
        name: str,
        edges: Dict[str, List[Edge]] = {},
        node_sid: int | None = None,
    ) -> None:
        """
        Init a new Node

        :param str name: Name of new node
        """
        if not name:
            raise ValueError("Name required to create new node")
        self.name = str(name)

        if edges:
            if not type(edges) == dict:
                raise TypeError(f"edges must be dict not {type(edges)}")
            self.edges = edges

        if node_sid:
            if not type(node_sid) == int:
                raise TypeError(f"node_sid must be int not {type(node_sid)}")
            self.node_sid = node_sid

    def __str__(self) -> str:
        return self.name

    def add_edges_from_nx_dict(self, edges: List) -> None:
        """
        Add a edges to this node from a list of networkx formatted dicts

        :param List edges: An list of dict of edges in networktx format
        :rtype: None
        """
        edge: Dict
        for edge in edges:
            if edge["source"] == self.name:
                if edge["target"] not in self.edges:
                    self.edges[edge["target"]] = []
                self.edges[edge["target"]].append(Edge.from_nx_dict(edge))

    def edges_to_list(self) -> List:
        """
        Return a JSON serializable list of edges

        :rtype: list
        """
        edges: List = []
        node_name: str
        for node_name in self.edges:
            edge: Edge
            for edge in self.edges[node_name]:
                edges.append(edge.to_dict())
        return edges

    @staticmethod
    def from_nx_dict(node: Dict) -> Node:
        """
        Return a new Node obj from a dict using networkx syntax

        :param Dict node: Node obj serialised as dict in networkx format
        :rtype: Node
        """
        new_node = Node(name=node["id"])
        if "node_sid" in node:
            new_node.node_sid = node["node_sid"]
        return new_node

    def no_of_edges(self) -> int:
        """
        Return the total number of edges this node has

        :rtype: int
        """
        count: int = 0
        node_name: str
        for node_name in self.edges:
            count += len(self.edges[node_name])
        return count

    def node_to_dict(self) -> Dict:
        """
        Return a JSON serializable dict of the node, without any edges

        :rtype: Dict
        """
        return {"id": self.name}

    def to_dict(self) -> Dict:
        """
        Return a JSON serializable dict of the object

        :rtype: Dict
        """
        data: Dict = {
            "edges": self.edges_to_list(),
            "name": self.name,
        }
        return data
