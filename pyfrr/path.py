from __future__ import annotations

import logging
from typing import Iterator, List

from .node import Edge, Node


class EdgePath(object):
    """
    A list of edges along a NodePath
    """

    def __init__(self: EdgePath, edge_path: List[Edge] = []) -> None:
        self.edge_path: List[Edge] = edge_path
        logging.debug(
            f"Init'd EdgePath {hex(id(self))} with {len(self)} edges: {self}"
        )

    def __contains__(self: EdgePath, edge: Edge) -> bool:
        return edge in self.edge_path

    def __getitem__(self: EdgePath, index: slice | int) -> List[Edge] | Edge:
        if isinstance(index, slice):
            return self.edge_path[index.start : index.stop : index.step]
        return self.edge_path[index]

    def __len__(self: EdgePath) -> int:
        return len(self.edge_path)

    def __nonzero__(self: EdgePath) -> bool:
        return bool(self.edge_path)

    def __repr__(self: EdgePath) -> str:
        return str([str(edge) for edge in self.edge_path])

    def append(self: EdgePath, edge: Edge) -> None:
        """
        Add a new edge to this edge path

        :param Edge edge: New Edge obj to add
        :rtype: None
        """
        if edge not in self.edge_path:
            self.edge_path.append(edge)

    def copy(self: EdgePath) -> EdgePath:
        """
        Return a copy of this obj

        :rtype: EdgePath
        """
        return EdgePath(self.edge_path.copy())

    def pop(self: EdgePath, i: int = -1) -> Edge:
        """
        Remove the edge at index i from this edge path and return it

        :param int i: Edge index to remove from list
        :rtype: Edge
        """
        return self.edge_path.pop(i)

    def source(self: EdgePath) -> Node:
        """
        The first node in the edge path

        :rtype: Node
        """
        return self.edge_path[0].local

    def target(self: EdgePath) -> Node:
        """
        The last node in the edge path

        :rtype: Node
        """
        return self.edge_path[-1].remote

    def weight(self: EdgePath) -> int:
        """
        Return the total weight of this EdgePath

        :rtype: int
        """
        total: int = 0
        edge: Edge
        for edge in self.edge_path:
            total += edge.weight
        return total


class EdgePaths(object):
    """
    A list of EdgePath's in weight order
    """

    def __init__(self: EdgePaths, edge_paths: List[EdgePath] = []) -> None:
        self.edge_paths: List[EdgePath] = []

        for edge_path in edge_paths:
            self.add_edge_path(edge_path)
        logging.debug(
            f"Init'd EdgePaths {hex(id(self))} with {len(self)} edge paths: "
            f"{self}"
        )

    def __getitem__(self: EdgePaths, index: int) -> EdgePath:
        return self.edge_paths[index]

    def __len__(self: EdgePaths) -> int:
        return len(self.edge_paths)

    def __nonzero__(self: EdgePaths) -> bool:
        return bool(self.edge_paths)

    def __repr__(self: EdgePaths) -> str:
        return str([str(edge_path) for edge_path in self.edge_paths])

    def add_edge_path(self: EdgePaths, edge_path: EdgePath) -> None:
        """
        Add the new edge path in descending weight order

        :param EdgeParth edge_path: The new edge path to be added
        :rtype: None
        """
        for i, existing_path in enumerate(self.edge_paths):
            if edge_path.weight() <= existing_path.weight():
                self.edge_paths.insert(i, edge_path)
                return
        self.edge_paths.append(edge_path)

    @staticmethod
    def expand_node_path(
        all_edge_paths: EdgePaths,
        edge_path: EdgePath,
        node_path: NodePath | Node,
    ) -> EdgePaths | None:
        """
        Recursively (DFS) expand a node path to a list of edge paths along the
        node path.

        :param EdgePaths all_edge_paths: The list of all edge paths
        :param Edgepath edge_path: The edge path currently being expanded
        :param NodePath node_path: The list of nodes to expand into edges
        :rtype: EdgePaths
        """
        assert type(node_path) == NodePath
        if len(node_path) < 2:
            return None

        for edge in [e for e in node_path.edges(0) if e not in edge_path]:
            edge_path.append(edge)
            if not EdgePaths.expand_node_path(
                all_edge_paths=all_edge_paths,
                edge_path=edge_path,
                node_path=node_path[1:],
            ):
                all_edge_paths.add_edge_path(edge_path.copy())
                edge_path.pop()

        if len(edge_path) > 0:
            edge_path.pop()
        return all_edge_paths

    @staticmethod
    def from_node_path(node_path: NodePath) -> EdgePaths:
        """
        Return all the edge paths for the NodePath

        :param NodePath node_path: A NodePath obj
        :rtype: EdgePaths
        """
        if len(node_path) > 1:
            logging.debug(f"Going to expand node path {node_path}")
            if edge_path := EdgePaths.expand_node_path(
                all_edge_paths=EdgePaths(edge_paths=[]),
                edge_path=EdgePath(edge_path=[]),
                node_path=node_path,
            ):
                return edge_path
        return EdgePaths()


class NodePath(object):
    """
    A list of nodes (from source to target) and the list of edge paths between
    these two nodes
    """

    def __init__(
        self: NodePath, expand_edges: bool = True, node_path: List[Node] = []
    ) -> None:
        self.node_path: List[Node] = node_path
        self.edge_paths: EdgePaths
        logging.debug(
            f"Init'd NodePath {hex(id(self))} with {len(self)} nodes: {self}"
        )
        if expand_edges:
            self.update_edge_paths()

    def __getitem__(self: NodePath, index: slice | int) -> NodePath | Node:
        """
        Currently if you slice a NodePath, all the edges need to be recalculated
        instead of being copied from the selected node onwards.
        FIXME / TODO
        """
        if isinstance(index, slice):
            return NodePath(
                node_path=self.node_path[index.start : index.stop : index.step],
            )
        return self.node_path[index]

    def __iter__(self: NodePath) -> Iterator:
        return self.node_path.__iter__()

    def __len__(self: NodePath) -> int:
        return len(self.node_path)

    def __nonzero__(self: NodePath) -> bool:
        return bool(self.node_path)

    def __repr__(self: NodePath) -> str:
        return str([str(node) for node in self.node_path])

    def add_node(self: NodePath, node: Node) -> None:
        """
        Add a new node to the end of the node path

        :param Node node: New node obj to append
        :rtype: None
        """
        if node not in self.node_path:
            self.node_path.append(node)

    def copy(self: NodePath) -> NodePath:
        """
        Return a copy of this obj

        :rtype: NodePath
        """
        return NodePath(node_path=self.node_path.copy())

    def pop(self: NodePath, i: int = -1) -> Node:
        """
        Remove the node at index i from this node path and return it

        :param int i: Node index to remove from list
        :rtype: Node
        """
        return self.node_path.pop(i)

    def edges(self: NodePath, i: int) -> List[Edge]:
        """
        Return the list of edges at the given index in the node path

        :rtype: List
        """
        return self.node_path[i].edges_toward_node(self.node_path[i + 1])

    def get_source(self: NodePath) -> Node:
        """
        Get the first node in this node path

        :rtype: Node
        """
        return self.node_path[0]

    def get_target(self: NodePath) -> Node:
        """
        Get the last node in this node path

        :rtype: Node
        """
        return self.node_path[-1]

    def no_edge_paths(self: NodePath) -> int:
        """
        The number of edge paths between the source and target node

        :rtype: int
        """
        return len(self.edge_paths)

    def set_source(self: NodePath, source: Node) -> None:
        """
        Set the first node in this NodePath.
        This will the existing path if one exists.

        :param Node source: Node to set as the source of the path.
        :rtype: None
        """
        if self.node_path:
            self.node_path = []
        self.node_path.append(source)

    def update_edge_paths(self: NodePath) -> None:
        """
        Update the edge paths for this node path

        :rtype: None
        """
        self.edge_paths = EdgePaths.from_node_path(self)


class NodePaths(object):
    """
    A list of NodePath's between the same source and target
    """

    def __init__(self: NodePaths, node_paths: List[NodePath] = []) -> None:
        self.node_paths: List[NodePath] = []
        for node_path in node_paths:
            self.add_node_path(node_path)

        logging.debug(
            f"Init'd NodePaths {hex(id(self))} with {len(self)} node paths"
        )

    def __getitem__(
        self: NodePaths, index: slice | int
    ) -> NodePaths | NodePath:
        if isinstance(index, slice):
            return NodePaths(
                self.node_paths[index.start : index.stop : index.step]
            )
        return self.node_paths[index]

    def __iter__(self: NodePaths) -> Iterator:
        return self.node_paths.__iter__()

    def __len__(self: NodePaths) -> int:
        return len(self.node_paths)

    def __nonzero__(self: NodePaths) -> bool:
        return bool(self.node_paths)

    def __repr__(self: NodePaths) -> str:
        return str([str(node_path) for node_path in self.node_paths])

    def add_node_path(self: NodePaths, node_path: NodePath) -> None:
        """
        Add a new NodePath obj to the list of NodePaths'

        :param NodePath node_path: The new node path to add
        :rtype: None
        """
        if self.node_paths:
            if (
                node_path.get_source() != self.node_paths[0].get_source()
                or node_path.get_target() != self.node_paths[0].get_target()
            ):
                raise ValueError(
                    f"Source and target nodes of new path ({node_path.get_source()}"
                    f" -> {node_path.get_target()}) don't match existing paths ("
                    f"{self.node_paths[0].get_source()} -> "
                    f"{self.node_paths[-1].get_target()})"
                )

        if node_path not in self.node_paths:
            self.node_paths.append(node_path)
