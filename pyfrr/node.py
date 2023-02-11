from __future__ import annotations

from typing import Dict, List


class Edge(object):
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

        if type(adj_sid) != int and type(adj_sid) != None:
            raise ValueError(
                f"adj_sid must be int or None, not {type(adj_sid)}"
            )
        self.adj_sid = adj_sid

        if type(weight) != int and weight != None:
            raise ValueError(f"weight must be int or None, not {type(weight)}")
        self.weight = weight

    def __repr__(self) -> str:
        attrs: Dict = {}
        if self.adj_sid:
            attrs["adj_sid"] = self.adj_sid
        if self.weight:
            attrs["weight"] = self.weight
        return f"{self.local} -> {self.remote}: {attrs}"

    def copy(self) -> Edge:
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

    def swap_nodes(self) -> None:
        """
        Reverse the source and targets of this edge

        :rtype: None
        """
        temp: Node = self.local
        self.local = self.remote
        self.remote = temp

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


class Node(object):
    def __init__(
        self,
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

    def __str__(self) -> str:
        return self.name

    def add_edge(self, edge: Edge) -> None:
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

    def add_neighbour(self, neighbour: Node) -> None:
        """
        Add a new neighbour to the lis tof neighbours

        :param Node neighbour: New neighbour to add
        :rtype: None
        """
        if neighbour not in self.neighbours:
            self.neighbours.append(neighbour)

    # def all_edges(self) -> Dict:
    #    """
    #    Return all the edges of this node
    #    """
    #    return self.edges

    def edges_to_list(self) -> List:
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

    def edges_toward_node(self, node: Node) -> List[Edge]:
        """
        Return the list of edges towards 'node'

        :param Node node: Node obj the local node has edges to
        :rtype: List
        """
        if node in self.edges:
            return self.edges[node]
        return []

    def get_name(self) -> str:
        """
        Return the name of this node

        :rtype: str
        """
        return self.name

    def get_neighbours(self) -> List[Node]:
        """
        Return a list of neighbours

        :rtype: List
        """
        return self.neighbours

    def no_of_edges(self) -> int:
        """
        Return the total number of edges this node has

        :rtype: int
        """
        count: int = 0
        node: Node
        for node in self.edges:
            count += len(self.edges[node])
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
