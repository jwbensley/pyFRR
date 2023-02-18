from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any, Iterator, List, TypeVar

from .node import Edge, Node
from .settings import Settings

BASE_PATH = TypeVar('BASE_PATH')


class BasePath(object):
    """
    Base class for *Path objects
    """

    def __init__(self: BasePath, path: List = []) -> None:
        self.path = path

    def __contains__(self: BasePath, item: Any) -> bool:
        return item in self.path

    """
    def __getitem__(self: BasePath, index: slice | int) -> BASE_PATH | Any:
        # Currently if you slice a NodePath, all the edges need to be recalculated
        # instead of being copied from the selected node onwards.
        # FIXME / TODO
        if isinstance(index, slice):
            return BasePath(
                path=self.path[index.start : index.stop : index.step],
            )
        return self.path[index]
    """

    def __iter__(self: BasePath) -> Iterator:
        return self.path.__iter__()

    def __len__(self: BasePath) -> int:
        return len(self.path)

    def __nonzero__(self: BasePath) -> bool:
        return bool(self.path)

    def __repr__(self: BasePath) -> str:
        return str([str(item) for item in self.path])

    def append(self: BasePath, item: Any) -> None:
        """
        Add a new itme to the end of the path

        :param Any item: New item obj to append
        :rtype: None
        """
        if item not in self.path:
            self.path.append(item)

    def copy(self: BASE_PATH) -> BASE_PATH:
        """
        Return a copy of this obj

        :rtype: BASE_PATH
        """
        return deepcopy(self)


class BasePaths(object):
    """
    Base class for *Paths objects
    """

    def __init__(self: BasePaths, paths: List = []) -> None:
        self.paths: List = paths

    def __getitem__(
        self: BasePaths, index: slice | int
    ) -> BasePaths | BasePath:
        if isinstance(index, slice):
            return BasePaths(self.paths[index.start : index.stop : index.step])
        return self.paths[index]

    def __iter__(self: BasePaths) -> Iterator:
        return self.paths.__iter__()

    def __len__(self: BasePaths) -> int:
        return len(self.paths)

    def __nonzero__(self: BasePaths) -> bool:
        return bool(self.paths)

    def __repr__(self: BasePaths) -> str:
        s: str = ""
        for path in self.paths:
            s += f"{path}\n"
        return s


class EdgePath(BasePath):
    """
    A list of edges along a NodePath
    """

    def __init__(self: EdgePath, path: List[Edge] = []) -> None:
        self.path: List[Edge] = path
        logging.debug(
            f"Init'd EdgePath {hex(id(self))} with {len(self)} edges: {self}"
        )

    """
    def __contains__(self: EdgePath, edge: Edge) -> bool:
        return edge in self.edge_path
    """

    def __getitem__(self: EdgePath, index: slice | int) -> List[Edge] | Edge:
        if isinstance(index, slice):
            return self.path[index.start : index.stop : index.step]
        return self.path[index]

    """
    def __len__(self: EdgePath) -> int:
        return len(self.edge_path)

    def __nonzero__(self: EdgePath) -> bool:
        return bool(self.edge_path)

    def __repr__(self: EdgePath) -> str:
        return str([str(edge) for edge in self.edge_path])
    """

    def append(self: EdgePath, edge: Edge) -> None:
        """
        Add a new edge to this edge path

        :param Edge edge: New Edge obj to add
        :rtype: None
        """
        if edge not in self.path:
            self.path.append(edge)

    def copy(self: EdgePath) -> EdgePath:
        """
        Return a copy of this obj

        :rtype: EdgePath
        """
        return EdgePath(self.path.copy())

    def pop(self: EdgePath, i: int = -1) -> Edge:
        """
        Remove the edge at index i from this edge path and return it

        :param int i: Edge index to remove from list
        :rtype: Edge
        """
        return self.path.pop(i)

    def source(self: EdgePath) -> Node:
        """
        The first node in the edge path

        :rtype: Node
        """
        return self.path[0].local

    def target(self: EdgePath) -> Node:
        """
        The last node in the edge path

        :rtype: Node
        """
        return self.path[-1].remote

    def weight(self: EdgePath) -> int:
        """
        Return the total weight of this EdgePath

        :rtype: int
        """
        total: int = 0
        edge: Edge
        for edge in self.path:
            total += edge.weight
        return total


class EdgePaths(BasePaths):
    """
    A list of EdgePath's stored in ascending in weight order
    """

    def __init__(self: EdgePaths, paths: List[EdgePath] = []) -> None:
        self.paths: List[EdgePath] = []

        for path in paths:
            self.add_edge_path(path)

        logging.debug(
            f"Init'd EdgePaths {hex(id(self))} with {len(self)} edge paths: "
            f"{self}"
        )

    def add_edge_path(self: EdgePaths, path: EdgePath) -> None:
        """
        Add the new edge path in ascending weight order

        :param EdgeParth path: The new edge path to be added
        :rtype: None
        """
        for i, existing_path in enumerate(self.paths):
            if path.weight() <= existing_path.weight():
                self.paths.insert(i, path)
                return
        self.paths.append(path)

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

    def get_lowest_edgepath_weight(self: EdgePaths) -> int:
        """
        Return the weigth of the lowest weighted EdgePath in this EdgePaths obj

        :rtype: int
        """
        if self.paths:
            return self.paths[0].weight()
        return Settings.INVALID_WEIGHT

    def get_lowest_weighted_paths(self: EdgePaths) -> EdgePaths:
        """
        Return a new EdgePaths obj with only the lowest weighted EdgePath's

        :rtype: EdgePaths
        """
        paths: EdgePaths = EdgePaths(paths=[])

        if self.paths:
            lowest_weight: int = self.paths[0].weight()
            for path in self.paths:
                if path.weight() == lowest_weight:
                    paths.add_edge_path(path)
                    continue
                break

        return paths

    @staticmethod
    def from_node_path(path: NodePath) -> EdgePaths:
        """
        Return all the edge paths for the NodePath

        :param NodePath node_path: A NodePath obj
        :rtype: EdgePaths
        """
        if len(path) > 1:
            logging.debug(f"Going to expand node path {path}")
            if edge_paths := EdgePaths.expand_node_path(
                all_edge_paths=EdgePaths(paths=[]),
                edge_path=EdgePath(path=[]),
                node_path=path,
            ):
                return edge_paths
        return EdgePaths()


class NodePath(BasePath):
    """
    A list of nodes (from source to target) and the list of edge paths between
    these two nodes
    """

    def __init__(
        self: NodePath, expand_edges: bool = True, path: List[Node] = []
    ) -> None:
        self.path: List[Node] = path
        self.edge_paths: EdgePaths

        logging.debug(
            f"Init'd NodePath {hex(id(self))} with {len(self)} nodes: {self}"
        )

        if expand_edges:
            self.update_edge_paths()

    def __getitem__(self: NodePath, index: slice | int) -> NodePath | Node:
        # Currently if you slice a NodePath, all the edges need to be recalculated
        # instead of being copied from the selected node onwards.
        # FIXME / TODO
        if isinstance(index, slice):
            return NodePath(
                path=self.path[index.start : index.stop : index.step],
            )
        return self.path[index]

    """
    def __iter__(self: NodePath) -> Iterator:
        return self.node_path.__iter__()

    def __len__(self: NodePath) -> int:
        return len(self.node_path)

    def __nonzero__(self: NodePath) -> bool:
        return bool(self.node_path)

    def __repr__(self: NodePath) -> str:
        return str([str(node) for node in self.node_path])
    """

    def append(self: NodePath, node: Node) -> None:
        """
        Add a new node to the end of the node path

        :param Node node: New node obj to append
        :rtype: None
        """
        if node not in self.path:
            self.path.append(node)

    def copy(self: NodePath) -> NodePath:
        """
        Return a copy of this obj

        :rtype: NodePath
        """
        return NodePath(path=self.path.copy())

    def edges(self: NodePath, i: int) -> List[Edge]:
        """
        Return the list of edges at the given index in the node path

        :rtype: List
        """
        return self.path[i].edges_toward_node(self.path[i + 1])

    def get_lowest_edgepath_weight(self: NodePath) -> int:
        """
        Return the weight of the lowest weighted EdgePath along this NodePath

        :rtype: int
        """
        return self.edge_paths.get_lowest_edgepath_weight()

    def get_source(self: NodePath) -> Node:
        """
        Get the first node in this node path

        :rtype: Node
        """
        return self.path[0]

    def get_target(self: NodePath) -> Node:
        """
        Get the last node in this node path

        :rtype: Node
        """
        return self.path[-1]

    def no_edge_paths(self: NodePath) -> int:
        """
        The number of edge paths between the source and target node

        :rtype: int
        """
        return len(self.edge_paths)

    def pop(self: NodePath, i: int = -1) -> Node:
        """
        Remove the node at index i from this node path and return it

        :param int i: Node index to remove from list
        :rtype: Node
        """
        return self.path.pop(i)

    def set_source(self: NodePath, source: Node) -> None:
        """
        Set the first node in this NodePath.
        This will erase the existing path if one exists.

        :param Node source: Node to set as the source of the path.
        :rtype: None
        """
        if self.path:
            self.path = []
        self.path.append(source)

    def update_edge_paths(self: NodePath) -> None:
        """
        Update the edge paths for this node path

        :rtype: None
        """
        self.edge_paths = EdgePaths.from_node_path(self)


class NodePaths(BasePaths):
    """
    A list of NodePath's between the same source and target
    """

    def __init__(self: NodePaths, paths: List[NodePath] = []) -> None:
        self.paths: List[NodePath] = paths

        logging.debug(
            f"Init'd NodePaths {hex(id(self))} with {len(self)} node paths"
        )

    def append(self: NodePaths, path: NodePath) -> None:
        """
        Add a new NodePath obj to the list of NodePaths'

        :param NodePath path: The new node path to add
        :rtype: None
        """
        self.validate_endpoints(
            source=path.get_source(), target=path.get_target()
        )

        if path not in self.paths:
            self.paths.append(path)

    def get_lowest_weight_nodepaths(self: NodePaths) -> NodePaths:
        """
        Return a NodePaths obj with only the lowest weight NodePath's from
        this NodePaths obj

        :rtype: NodePaths
        """
        if not self.paths:
            return NodePaths(paths=[])

        lowest_weight: int = Settings.HEIGHTEST_WEIGHT
        node_paths: NodePaths = NodePaths(paths=[])

        path: NodePath
        for path in self.paths:
            node_path_weight: int = path.get_lowest_edgepath_weight()

            if lowest_weight == Settings.HEIGHTEST_WEIGHT:
                lowest_weight = node_path_weight
            if node_path_weight < lowest_weight:
                node_paths = NodePaths(paths=[path])
            elif node_path_weight == lowest_weight:
                node_paths.append(path)

        return node_paths

    def get_source(self: NodePaths) -> Node | None:
        """
        Return the source node of the NodePath's in this NodePaths obj

        :rtype: Node
        """
        if self.paths:
            return self.paths[0].get_source()
        return None

    def get_target(self: NodePaths) -> Node | None:
        """
        Return the target node of the NodePath's in this NodePaths obj

        :rtype: Node
        """
        if self.paths:
            return self.paths[0].get_target()
        return None

    def validate_endpoints(self: NodePaths, source: Node, target: Node) -> None:
        """
        Confirm that the source and target nodes are the same as the source and
        target nodes which this NodePaths object represents paths between

        :param Node source: Source node to check against this NodePaths obj
        :param Node target: Target node to check against this NodePaths obj
        :rtype: None
        """
        if self.paths:
            if source != self.get_source() or target != self.get_target():
                raise ValueError(
                    f"Source and target nodes ({source} -> {target}) don't "
                    f"match existing paths ({self.get_source()} -> "
                    f"{self.get_target()})"
                )
