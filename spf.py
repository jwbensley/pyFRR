import networkx as nx
import os
from diagram import Diagram


class spf:
    """This class provides simple shortest path first calculations"""

    def __init__(self, debug=0):
        """
        Init the Shortest Path class.

        :param int debug: debug level, 0 is disabled.
        :return None: __init__ shouldn't return anything
        :rtype: None
        """
        self.debug = debug
        self.diagram = Diagram(debug=self.debug)
        self.path_types = ["spf_metric"]

    def draw(self, graph, outdir, topology):
        """
        Loop over the generated topologies and render them as diagram files.

        :param networkx.Graph graph: NetworkX graph object
        :param str outdir: string of the root output directory path
        :param dict topology: topology paths dict
        :return bool True: True if all diagrams rendered otherwise False
        :rtype: bool
        """

        self.diagram.gen_sub_dirs(graph, outdir, self.path_types, topology)

        for src, dst in [
            (s, d) for d in graph.nodes for s in graph.nodes if s != d
        ]:

            for path_type in self.path_types:
                if path_type not in topology[src][dst]:
                    continue

                if len(topology[src][dst][path_type]) > 0:
                    spf_graph = graph.copy()

                    for path in topology[src][dst][path_type]:
                        spf_graph = self.diagram.highlight_links(
                            "green",
                            spf_graph,
                            path,
                        )
                        spf_graph = self.diagram.highlight_nodes(
                            "green",
                            spf_graph,
                            path,
                        )

                    spf_graph = self.diagram.highlight_src_dst(
                        "lightblue", dst, spf_graph, src
                    )
                    # Add labels to links showing their cost
                    spf_graph = self.diagram.label_link_weights(spf_graph)

                    self.diagram.gen_diagram(
                        (src + "_" + dst + "_" + path_type),
                        spf_graph,
                        os.path.join(outdir, src, path_type),
                    )

    def gen_metric_cost(self, dst, graph, src):
        """
        Return the cost for shortest path(s) from src to dst in "graph".

        :param str dst: Destination node name in graph
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node name in graph
        :return cost: int cost of best path(s) from src to dst
        :rtype: int
        """

        try:
            cost = nx.shortest_path_length(
                graph, source=src, target=dst, weight="weight"
            )
        except nx.exception.NetworkXNoPath:
            cost = -1

        if self.debug > 0:
            print(
                f"Shortest path(s) from {src} to {dst} have cost: {cost}"
            )

        return cost

    def gen_metric_paths(self, dst, graph, src):
        """
        Return all the equal cost shortest paths from src to dst in graph.

        :param str dst: Destination node name in graph
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node name in graph
        :return paths: list of shortest paths from src to dst
        :rtype: list
        """

        """
        all_shortest_paths() returns a generator, which produces a list for
        each of the equal cost shortest paths. The end result is a list of
        lists.
        """
        try:
            paths = list(
                nx.all_shortest_paths(
                    graph, source=src, target=dst, weight="weight"
                )
            )
        except nx.exception.NetworkXNoPath:
            paths = []

        if self.debug > 0:
            hop_count = [len(path) for path in paths]
            links = [
                [(path[i], path[i + 1]) for i in range(0, len(path) - 1)]
                for path in paths
            ]

            if len(paths) == 0:
                print(f"No path from {src} to {dst}")
            elif len(paths) == 1:
                print(
                    f"1 shortest path from {src} to {dst}:\n"
                    f"{hop_count[0]} hops: {paths[0]}, "
                    f"{len(links[0])} link(s): {links[0]}"
                )
            elif len(paths) > 1:
                print(
                    f"{len(paths)} equal cost shortest paths from "
                    f"{src} to {dst}:\n"
                    f"With the following hop count in each: {hop_count}\n"
                    f"With the following link(s) in each: {links}"
                )

        return paths

    def gen_nei_metric_paths(self, dst, graph, src):
        """
        Return the shortest metric (not hop count) based path(s) from src to
        each if it's neighbours, and from each neighbour of src toward dst.

        :param str dst: Destination node name in graph
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node name in graph
        :return paths: dict of list of best paths keyed by src and dst
        :rtype: list
        """

        paths = {}
        paths[src] = {}
        paths[dst] = {}

        for nei in graph.neighbors(src):

            if nei == dst:
                continue

            if nei not in paths[src]:
                paths[src][nei] = self.gen_metric_paths(
                    dst=nei, graph=graph, src=src
                )
            if nei not in paths[dst]:
                paths[dst][nei] = self.gen_metric_paths(
                    dst=dst, graph=graph, src=nei
                )

        if self.debug > 0:
            print(
                f"Paths from {src} each neighbour of {src}: "
                f"{paths[src]}"
            )
            print(
                f"Paths from each neighbour of {src} to {dst}: "
                f"{paths[dst]}"
            )

        return paths

    def gen_path_cost(self, graph, path):
        """
        Return the cost for the explicit "path" through "graph".

        :param networkx.Graph graph: NetworkX graph object
        :param list path: List of nodes in graph
        :return cost: int cost of the explicit path in graph
        :rtype: int
        """

        cost = 0
        for idx, node in enumerate(path):
            if idx < (len(path) - 1):
                cost += graph.edges[node, path[idx + 1]]["weight"]

        if self.debug > 0:
            print(
                f"Explicit path {path} has cost: {cost}"
            )

        return cost

    def init_topo(self, graph, topo):
        """
        Create empty dict keys for all possible paths this class can generate

        :return None:
        :rtype: None
        """

        for src in graph.nodes:
            for dst in graph.nodes:
                if src == dst:
                    continue

                for path_type in self.path_types:
                    if path_type not in topo[src][dst]:
                        topo[src][dst][path_type] = []
