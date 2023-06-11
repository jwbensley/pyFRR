from __future__ import annotations

import logging
from typing import Iterator, List, Type, TypeVar, Union

from .node import Edge, Node
from .settings import Settings

BASE_TYPE = TypeVar("BASE_TYPE", Edge, Node)
BASE_PATH = TypeVar("BASE_PATH", bound="BasePath")
BASE_PATHS = TypeVar("BASE_PATHS", bound="BasePaths")

logger = logging.getLogger(__name__)


class BasePath:
    """
    Base class for *Path objects
    """

    def __init__(self: BASE_PATH, path: List = []) -> None:
        self.path: List = path
        self.path_type: Type

    def __contains__(self: BASE_PATH, item: BASE_TYPE) -> bool:
        return item in self.path

    def __iter__(self: BASE_PATH) -> Iterator:
        return self.path.__iter__()

    def __len__(self: BASE_PATH) -> int:
        return len(self.path)

    def __nonzero__(self: BASE_PATH) -> bool:
        return bool(self.path)

    def __str__(self: BASE_PATH) -> str:
        if not self.path:
            return ""

        return (
            f"Weight {self.get_weight()}: {[str(item) for item in self.path]}"
        )

    def append(self: BASE_PATH, item: BASE_TYPE) -> None:
        """
        Add a new itme to the end of the path

        :param BASE_TYPE item: New item obj to append
        :rtype: None
        """
        if type(item) != self.path_type:
            raise ValueError(
                f"Can't append item of type {type(item)} to path of type "
                f"{type(self)}"
            )
        if item not in self.path:
            self.path.append(item)

    def copy(self: BASE_PATH) -> BASE_PATH:
        """
        Return a copy of this obj

        :rtype: BASE_PATH
        """
        return self.__class__(path=self.path.copy())

    def get_weight(self: BASE_PATH) -> int:
        return 0

    def pop(self: BASE_PATH, i: int = -1) -> BASE_TYPE:
        """
        Remove the item at path index i from and return it

        :param int i: Item index to remove from list
        :rtype: Edge or Node
        """
        return self.path.pop(i)

    def slice(
        self: BASE_PATH,
        start: int = 0,
        stop: int | None = None,
        step: int = 1,
    ) -> BASE_PATH:
        """
        Seperate this from __getitem__ due to the type hinting mess it creates
        when __getitem__ has to return a slice or a single item

        Currently if you slice a NodePath, all the edges need to be recalculated
        instead of being copied from the selected node onwards.
        FIXME / TODO

        :param slice index: Index range to slice from/to with step size
        :rtype: BASE_PATH
        """
        return self.__class__(path=self.path[start:stop:step])


class BasePaths:
    """
    Base class for *Paths objects
    """

    class ErrorNoPathsDefined(Exception):
        pass

    def __init__(self: BASE_PATHS, paths: List = []) -> None:
        self.paths: List = paths

    def __getitem__(self: BASE_PATHS, index: int) -> Union[NodePath, EdgePath]:
        """
        Support for slicing is in slice()
        """
        return self.paths[index]

    def __iter__(self: BASE_PATHS) -> Iterator:
        return self.paths.__iter__()

    def __len__(self: BASE_PATHS) -> int:
        return len(self.paths)

    def __nonzero__(self: BASE_PATHS) -> bool:
        return bool(self.paths)

    def __str__(self: BASE_PATHS) -> str:
        if not self.paths:
            return ""

        s: str = ""
        for path in self.paths:
            s += f"{path}\n"
        return s

    def slice(
        self: BASE_PATHS,
        start: int = 0,
        stop: int | None = None,
        step: int = 1,
    ) -> BASE_PATHS:
        """
        Seperate this from __getitem__ due to the type hinting mess it creates
        when __getitem__ has to return a slice or a single item

        :param slice index: Index range to slice from/to with step size
        :rtype: BASE_PATHS
        """
        return self.__class__(paths=self.paths[start:stop:step])


class EdgePath(BasePath):
    """
    A list of Edges along a NodePath
    """

    log_prefix: str = __name__

    def __init__(self: EdgePath, path: List[Edge] = []) -> None:
        self.path: List[Edge] = path
        self.path_type: Type[Edge] = Edge
        logger.log(
            level=Settings.LOG_DEV_LEVEL,
            msg=f"{EdgePath.log_prefix}: Init'd {self.__class__} @{hex(id(self))} "
            f"with path len {len(self)}",
        )

    def __getitem__(self: EdgePath, index: int) -> Edge:
        """
        Support for slicing is in slice()

        :param int index: Index in path to return
        :rtype: Edge
        """
        return self.path[index]

    def get_source(self: EdgePath) -> Node:
        """
        The first node in the edge path

        :rtype: Node
        """
        return self.path[0].local

    def get_target(self: EdgePath) -> Node:
        """
        The last node in the edge path

        :rtype: Node
        """
        return self.path[-1].remote

    def get_weight(self: EdgePath) -> int:
        """
        Return the total weight of this EdgePath

        :rtype: int
        """
        total: int = 0
        item: Edge
        for item in self.path:
            total += item.get_weight()
        return total


class EdgePaths(BasePaths):
    """
    A list of EdgePath's stored in ascending in weight order
    """

    log_prefix: str = __name__

    def __init__(self: EdgePaths, paths: List[EdgePath] = []) -> None:
        self.paths: List[EdgePath] = paths

        for path in paths:
            self.append(path)

        logger.log(
            level=Settings.LOG_DEV_LEVEL,
            msg=f"{EdgePaths.log_prefix}: Init'd {type(self)} @{hex(id(self))} "
            f"with {len(self)} paths",
        )

    def append(self: EdgePaths, path: EdgePath) -> None:
        """
        Add the new edge path in ascending weight order

        :param EdgeParth path: The new edge path to be added
        :rtype: None
        """
        for i, existing_path in enumerate(self.paths):
            if path.get_weight() <= existing_path.get_weight():
                self.paths.insert(i, path)
                return
        self.paths.append(path)

    @staticmethod
    def expand_node_path(
        all_edge_paths: EdgePaths,
        edge_path: EdgePath,
        node_path: NodePath,
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

        for edge in [e for e in node_path.get_edges(0) if e not in edge_path]:
            edge_path.append(edge)
            if not EdgePaths.expand_node_path(
                all_edge_paths=all_edge_paths,
                edge_path=edge_path,
                node_path=node_path.slice(1),
            ):
                all_edge_paths.append(edge_path.copy())
                edge_path.pop()

        if len(edge_path) > 0:
            edge_path.pop()
        return all_edge_paths

    def get_lowest_path_weight(self: EdgePaths) -> int:
        """
        Return the weight of the lowest EdgePath in this EdgePaths obj

        :rtype: int
        """
        if self.paths:
            return self.paths[0].get_weight()
        return 0

    def get_lowest_weighted_paths(self: EdgePaths) -> EdgePaths:
        """
        Return a new EdgePaths obj with only the lowest weighted EdgePath's

        :rtype: EdgePaths
        """
        paths: EdgePaths = EdgePaths(paths=[])

        if not self.paths:
            return paths

        lowest_weight: int = self.get_lowest_path_weight()
        for path in self.paths:
            if path.get_weight() == lowest_weight:
                paths.append(path)
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
            logger.log(
                level=Settings.LOG_DEV_LEVEL,
                msg=f"{EdgePaths.log_prefix}: Going to expand node path {path}",
            )
            if edge_paths := EdgePaths.expand_node_path(
                all_edge_paths=EdgePaths(paths=[]),
                edge_path=EdgePath(path=[]),
                node_path=path,
            ):
                return edge_paths
        return EdgePaths()


class NodePath(BasePath):
    """
    A list of Nodes (from source to target) and the list of EdgePaths between
    these two nodes
    """

    log_prefix: str = __name__

    def __init__(
        self: NodePath, expand_edges: bool = True, path: List[Node] = []
    ) -> None:
        self.path: List[Node] = path
        self.down_protecting: bool = False
        self.link_protecting: bool = False
        self.node_protecting: bool = False
        self.edge_paths: EdgePaths = EdgePaths()
        self.path_type: Type[Node] = Node
        logger.log(
            level=Settings.LOG_DEV_LEVEL,
            msg=f"{NodePath.log_prefix}: Init'd {type(self)} @{hex(id(self))} with "
            f"{len(self)} paths",
        )

        if expand_edges:
            self.update_edge_paths()

    def __getitem__(self: NodePath, index: int) -> Node:
        """
        Support for slicing is in slice()

        :param int index: Index in path to return
        :rtype: Node
        """
        return self.path[index]

    def get_edges(self: NodePath, i: int) -> List[Edge]:
        """
        Return the list of edges at the given index in the node path

        :rtype: List
        """
        return self.path[i].edges_toward_node(self.path[i + 1])

    def get_lowest_path_weight(self: NodePath) -> int:
        """
        Return the weight of the lowest weighted EdgePath along this NodePath

        :rtype: int
        """
        return self.edge_paths.get_lowest_path_weight()

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

    def get_weight(self: NodePath) -> int:
        """
        Return the weight of the lowest weighted EdgePath along this NodePath

        :rtype: int
        """
        return self.get_lowest_path_weight()

    def is_down_protecting(self: NodePath) -> bool:
        """
        Is this NodePath downstream path protecting
        """
        return self.down_protecting

    def is_link_protecting(self: NodePath) -> bool:
        """
        Is this NodePath link protecting
        """
        return self.link_protecting

    def is_node_protecting(self: NodePath) -> bool:
        """
        Is this NodePath node protecting
        """
        return self.node_protecting

    def no_edge_paths(self: NodePath) -> int:
        """
        The number of edge paths between the source and target node

        :rtype: int
        """
        return len(self.edge_paths)

    def prepend(self: NodePath, node: Node) -> None:
        """
        Prepend a node to this NodePath
        """
        self.path = [node] + self.path
        self.update_edge_paths()

    def set_down_protecting(self: NodePath, protecting: bool) -> None:
        """
        Set this NodePath's downstream protecting state
        """
        self.down_protecting = protecting

    def set_link_protecting(self: NodePath, protecting: bool) -> None:
        """
        Set this NodePath's is link protecting state
        """
        self.link_protecting = protecting

    def set_node_protecting(self: NodePath, protecting: bool) -> None:
        """
        Set this NodePath's is node protecting state
        """
        self.node_protecting = protecting

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
    A list of NodePath's between the same source and target,
    sorted in ascending weight order
    """

    log_prefix: str = __name__

    def __init__(self: NodePaths, paths: List[NodePath] = []) -> None:
        self.paths: List[NodePath] = paths

        logger.log(
            level=Settings.LOG_DEV_LEVEL,
            msg=f"{NodePaths.log_prefix}: Init'd {type(self)} @{hex(id(self))} "
            f"with {len(self)} paths",
        )

    def append(self: NodePaths, path: NodePath) -> None:
        """
        Add a new NodePath obj to the list of NodePaths, in weighted order

        :param NodePath path: The new node path to add
        :rtype: None
        """
        self.validate_endpoints(
            source=path.get_source(), target=path.get_target()
        )

        if path not in self.paths:
            for i, existing_path in enumerate(self.paths):
                if path.get_weight() <= existing_path.get_weight():
                    self.paths.insert(i, path)
                    return
            self.paths.append(path)

    def get_lowest_path_weight(self: NodePaths) -> int:
        """
        Return the weight of the lowest weighted NodePath in this NodePaths obj

        :rtype: int
        """
        if not self.paths:
            return 0

        lowest_weight: int = Settings.HEIGHTEST_WEIGHT
        for path in self.paths:
            weight: int = path.get_lowest_path_weight()
            if weight < lowest_weight:
                lowest_weight = weight
        return lowest_weight

    def get_lowest_weighted_paths(self: NodePaths) -> NodePaths:
        """
        Return a NodePaths obj with only the lowest weight NodePath's from
        this NodePaths obj

        :rtype: NodePaths
        """
        lowest_weight: int = Settings.HEIGHTEST_WEIGHT
        paths: NodePaths = NodePaths(paths=[])

        if not self.paths:
            return paths

        path: NodePath
        for path in self.paths:
            path_weight: int = path.get_lowest_path_weight()

            if path_weight < lowest_weight:
                lowest_weight = path_weight
                paths = NodePaths(paths=[path])
            elif path_weight == lowest_weight:
                paths.append(path)
        return paths

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

    def validate_endpoints(
        self: NodePaths, source: Node, target: Node
    ) -> None:
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
