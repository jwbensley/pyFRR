from __future__ import annotations

from typing import Any, Dict, List

from .settings import Settings


class Edge:
    def __init__(
        self,
        local: Node,
        remote: Node,
        adj_sid: int | None = None,
        weight: int = Settings.DEFAULT_WEIGHT,
    ) -> None:
        if not local or not remote:
            raise ValueError("local and remote must be defined")

        self.local = local
        self.remote = remote

        if type(adj_sid) != int and adj_sid != None:
            raise ValueError(
                f"adj_sid must be int or None, not {type(adj_sid)}"
            )
        self.adj_sid = adj_sid

        if type(weight) != int:
            raise ValueError(f"weight must be int, not {type(weight)}")
        self.weight = weight

    def __str__(self: Edge) -> str:
        attrs: Dict = {}
        if self.adj_sid:
            attrs["adj_sid"] = self.adj_sid
        if self.weight:
            attrs["weight"] = self.weight
        return f"{self.local} -> {self.remote}: {attrs}"

    def copy(self: Edge) -> Edge:
        """
        Return a copy of this Edge

        :rtype: Edge
        """
        return Edge(
            local=self.local,
            remote=self.remote,
            adj_sid=self.adj_sid,
            weight=self.weight,
        )

    @staticmethod
    def from_dict(nodes: Dict[str, Node], edge: Dict) -> Edge:
        """
        Return an Edge obj from a dict

        :param Dict node_list: Dict of nodes the edge connects
        :param Dict edge: A NetworkX syntax link object
        :rtype: Edge
        """
        return Edge(
            local=nodes[edge["source"]],
            remote=nodes[edge["target"]],
            adj_sid=edge["adj_sid"] if "adj_sid" in edge else None,
            weight=edge["weight"] if "weight" in edge else None,
        )

    def get_weight(self: Edge) -> int:
        """
        Return the weight of this edge

        :rtype: int
        """
        return self.weight

    def swap_nodes(self: Edge) -> None:
        """
        Reverse the source and targets of this edge

        :rtype: None
        """
        self.local, self.remote = self.remote, self.local

    def to_dict(self: Edge) -> Dict[str, Any]:
        """
        Return the Edge serialised as dictionary

        :rtype: Dict
        """
        d: Dict = {
            "source": str(self.local),
            "target": str(self.remote),
        }
        if self.adj_sid:
            d["adj_sid"] = self.adj_sid
        if self.weight:
            d["weight"] = self.weight
        return d


class Node:
    def __init__(
        self: Node,
        name: str,
        edges: Dict[Node, List[Edge]] = {},
        neighbours: List[Node] = [],
        node_sid: int | None = None,
    ) -> None:
        """
        Init a new Node

        :param str name: Name of new node
        :param Dict edges: Dict of edges towards each neighbour node
        :param List neighbours: List of direct neighbour nodes
        :param int node_sid: SR node SID
        :rtype: None
        """
        if not name:
            raise ValueError("Name required to create new node")
        self.name = str(name)

        if not type(edges) == dict:
            raise TypeError(f"edges must be dict not {type(edges)}")
        self.edges = edges

        if not type(neighbours) == list:
            raise TypeError(f"neighbours must be list not {type(neighbours)}")
        self.neighbours = neighbours

        if type(node_sid) != int and node_sid != None:
            raise TypeError(
                f"node_sid must be int or None, not {type(node_sid)}"
            )
        self.node_sid = node_sid

    def __str__(self: Node) -> str:
        return self.name

    def add_edge(self: Node, edge: Edge) -> None:
        """
        Add a new edge toward a specific neighbour

        :param Edge edge: The new edge to add
        :rtype: None
        """
        if edge.remote not in self.edges:
            self.edges[edge.remote] = []
            self.add_neighbour(edge.remote)
            edge.remote.add_neighbour(edge.local)
        if edge not in self.edges[edge.remote]:
            self.edges[edge.remote].append(edge)

    def add_neighbour(self: Node, neighbour: Node) -> None:
        """
        Add a new neighbour to the lis tof neighbours

        :param Node neighbour: New neighbour to add
        :rtype: None
        """
        if neighbour not in self.neighbours:
            self.neighbours.append(neighbour)

    def edges_to_list(self: Node) -> List:
        """
        Return a JSON serializable list of edges

        :rtype: list
        """
        edges: List = []
        node: Node
        for node in self.edges:
            edge: Edge
            for edge in self.edges[node]:
                edges.append(edge.to_dict())
        return edges

    def edges_toward_node(self: Node, node: Node) -> List[Edge]:
        """
        Return the list of edges towards 'node'

        :param Node node: Node obj the local node has edges to
        :rtype: List
        """
        if node in self.edges:
            return self.edges[node]
        return []

    @staticmethod
    def from_dict(node: Dict[str, Any]) -> Node:
        """
        Return a new Node obj from a dict

        :param Dict nx_node: Node obj serialised as dict in networkx format
        :rtype: Node
        """
        return Node(
            edges={},
            name=node["id"],
            neighbours=[],
            node_sid=node["node_sid"] if "node_sid" in node else None,
        )

    def get_name(self: Node) -> str:
        """
        Return the name of this node

        :rtype: str
        """
        return self.name

    def get_neighbours(self: Node) -> List[Node]:
        """
        Return a list of neighbours

        :rtype: List
        """
        return self.neighbours

    def no_of_edges(self: Node) -> int:
        """
        Return the total number of edges this node has

        :rtype: int
        """
        count: int = 0
        node: Node
        for node in self.edges:
            count += len(self.edges[node])
        return count

    def node_to_dict(self: Node) -> Dict[str, Any]:
        """
        Return a JSON serializable dict of the node, without any edges

        :rtype: Dict
        """
        d: Dict = {"id": self.name}
        if self.node_sid:
            d["node_sid"] = self.node_sid
        return d

    def to_dict(self: Node) -> Dict[str, Any]:
        """
        Return a JSON serializable dict of the object

        :rtype: Dict
        """
        data: Dict = {
            "edges": self.edges_to_list(),
            "name": self.name,
        }
        return data
