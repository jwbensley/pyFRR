import networkx as nx
import os
from diagram import Diagram
from spf import spf


class lfa:
    """This class provides RFC5286 lfa calculations"""

    def __init__(self, debug=0):
        """
        Init the lfa class.

        :param int debug: debug level, 0 is disabled.
        :return None: __init__ shouldn't return anything
        :rtype: None
        """
        self.debug = debug
        self.diagram = Diagram(debug=self.debug)
        self.path_types = ["lfas_dstream", "lfas_link", "lfas_node"]
        self.spf = spf(debug=self.debug)

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
                    frr_graph = graph.copy()

                    # Highlight the failed first-hop link(s) as red
                    for path in topology[src][dst]["cost"]:
                        frr_graph = self.diagram.highlight_fh_link(
                            "red",
                            frr_graph,
                            path,
                        )

                    # Highlight the failed first-hop node(s) as red
                    if path_type == "lfas_dstream":
                        for path in topology[src][dst]["cost"]:
                            frr_graph = self.diagram.highlight_fh_node(
                                "red",
                                frr_graph,
                                path,
                            )
                    elif path_type == "lfas_node":
                        for path in topology[src][dst]["cost"]:
                            frr_graph = self.diagram.highlight_fh_node(
                                "red",
                                frr_graph,
                                path,
                            )

                    for path in topology[src][dst][path_type]:
                        frr_graph = self.diagram.highlight_links(
                            "green",
                            frr_graph,
                            path,
                        )
                        frr_graph = self.diagram.highlight_nodes(
                            "green",
                            frr_graph,
                            path,
                        )

                    frr_graph = self.diagram.highlight_src_dst(
                        "lightblue", dst, frr_graph, src
                    )
                    # Add labels to links showing their cost
                    frr_graph = self.diagram.label_link_weights(frr_graph)

                    self.diagram.gen_diagram(
                        (src + "_" + dst + "_" + path_type),
                        frr_graph,
                        os.path.join(outdir, src, path_type),
                    )

    def gen_metric_paths(self, dst, graph, src):
        """
        Return all lfa paths between the src and dst nodes in graph, based on
        link metric (not hop count), which provide link, downstream, or node
        protection, and return all alternate paths in a dict of lists keyed by
        lfa path protection type.

        :param str dst: Destination node name in graph
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node name in graph
        :return lfas: dict of lists keyed by lfa type
        :rtype: dict
        """

        lfas = {"lfas_link": [], "lfas_dstream": [], "lfas_node": []}
        if self.debug > 0:
            print(f"Calculating for lfa paths from {src} to {dst}")
        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)

        # Loop over each neighbour to check if each one is an lfa candidate
        for nei in graph.neighbors(src):

            # If dst is directly connceted
            if nei == dst:
                continue

            if self.debug > 1:
                print(f"Checking for lfa paths via {nei}")

            # This nei is the next-hop for the current best path(s)
            if nei in [path[1] for path in s_d_paths]:
                if self.debug > 1:
                    print(
                        f"Rejected lfas via next-hop {nei}, it is a next-hop "
                        f"in the current best path(s): {s_d_paths}"
                    )
                continue

            """
            ECMP may be used meaning src has multiple equal cost best paths to
            dst. And/or, nei may have multiple equal cost best paths to dst.
            Regardless, of the number of paths, they are the same cost, so only
            check the cost of the first best path of src against the first best
            path of nei.
            """
            nh = s_d_paths[0][1]

            try:
                n_d_cost = nx.dijkstra_path_length(graph, source=nei, target=dst)
                n_s_cost = nx.dijkstra_path_length(graph, source=nei, target=src)
                s_d_cost = nx.dijkstra_path_length(graph, source=src, target=dst)
                n_nh_cost = nx.dijkstra_path_length(graph, source=nei, target=nh)
                nh_d_cost = nx.dijkstra_path_length(graph, source=nh, target=dst)
            except nx.exception.NetworkXNoPath:
                # There isn't connectivity between the nodes; src, dst, nh, nei
                continue

            if self.debug > 1:
                print(
                    f"{nei} -> {dst}: {n_d_cost}\n"
                    f"{nei} -> {src}: {n_s_cost}\n"
                    f"{src} -> {dst}: {s_d_cost}\n"
                    f"{nei} -> {nh}: {n_nh_cost}\n"
                    f"{nh} -> {dst}: {nh_d_cost}"
                )

            link_prot = False
            down_prot = False
            node_prot = False

            """
            RFC5286:
            Inequality 1: Loop-Free Criterion
            A neighbor N of source S can provide a loop-free alternate (lfa)
            toward destination D, that is link protecting, iff:
            Distance_opt(N, D) < Distance_opt(N, S) + Distance_opt(S, D)

            In this scenario, N's cost to D is lower than N's cost to S + S's
            cost to D, so N must have an alternative path to D not via S, but
            S and N might be sharing the same next-hop router, and N simply
            has another link to that shared next-hop router, so it is link
            protecting only, for S's link to it's next-hop.
            """
            if n_d_cost < (n_s_cost + s_d_cost):
                if self.debug > 1:
                    print(
                        f"{nei} to {dst} < ({nei} to {src} + {src} to {dst}), "
                        f"{n_d_cost} < {n_s_cost+s_d_cost}"
                    )

                # nei protects src against link failure to next-hop toward dst
                link_prot = True

            """
            RFC5286:
            Inequality 2: Downstream Path Criterion
            A neighbor N of source S can provide a loop-free alternate (lfa)
            to downstream paths of D, which could be link or node protecting,
            iff:
            Distance_opt(N, D) < Distance_opt(S, D)

            In this scenario, N's cost to D is lower than S's so N won't route
            back to S. This is basic loop avoidance gaurenteed but it doesn't
            restrict the lfa path to be link protecting or node protecting.
            This scenario is usually used to provide protection for a specific
            downstream prefix of node D rather than S's next-hop node or link
            toward D.
            """
            if n_d_cost < (s_d_cost):
                if self.debug > 1:
                    print(
                        f"{nei} to {dst} < {src} to {dst}: "
                        f"{n_d_cost} < {n_s_cost}"
                    )

                # nei protects src against failure of link or node toward dst
                down_prot = True

            """
            RFC5286:
            Inequality 3: Criteria for a Node-Protecting Loop-Free Alternate
            For an alternate next-hop N to protect against node failure of a
            primary neighbor E for destination D, N must be loop-free with
            respect to both E and D.
            Distance_opt(N, D) < Distance_opt(N, E) + Distance_opt(E, D)

            In this scenario, neighbour N of source router S, uses a different
            next-hop router toward destination D, than router E which is S's
            next-hop router toward D. This provides node protection against S's
            next-hop router E.
            """
            if n_d_cost < (n_nh_cost + nh_d_cost):
                if self.debug > 1:
                    print(
                        f"{nei} to {dst} < ({nei} to {nh} + {nh} to {dst}), "
                        f"{n_d_cost} < {n_nh_cost+nh_d_cost}"
                    )
                # nei protects src against next-hop node failure toward dst
                node_prot = True

            # nei might have multiple equal-cost best paths to dst
            n_d_paths = self.spf.gen_metric_paths(
                dst=dst, graph=graph, src=nei
            )

            for n_d_path in n_d_paths:

                if link_prot:
                    # Append src to n_d_path because it starts from nei
                    if n_d_path[0] != src:
                        n_d_path.insert(0, src)
                    lfas["lfas_link"].append(n_d_path)
                    if self.debug > 1:
                        print(
                            f"New link protecting lfa from {src} to "
                            f"{dst} via {nei}, protects against link "
                            f"{src}-{nh}: {n_d_path}"
                        )

                if down_prot:
                    # Append src to n_d_path because it starts from nei
                    if n_d_path[0] != src:
                        n_d_path.insert(0, src)
                    lfas["lfas_dstream"].append(n_d_path)
                    if self.debug > 1:
                        print(f"New downstream protecting lfa: {n_d_path}")

                if node_prot:
                    """
                    In order to protect pre-failure ECMP best-paths, check that
                    this node protecting path doesn't overlap with any of the
                    ECMP next-hop nodes
                    """
                    s_d_fhs = [path[1] for path in s_d_paths]
                    overlap = [
                        fh
                        for fh in s_d_fhs
                        for n_d_path in n_d_paths
                        if fh in n_d_path
                    ]
                    if overlap:
                        if self.debug > 1:
                            print(
                                f"lfa path {n_d_path} is not node protecting "
                                f"against {overlap} from {src} to {dst}"
                            )
                        continue

                    lfas["lfas_node"].append(n_d_path)
                    if self.debug > 1:
                        print(
                            f"New node protecting path from {src} to {dst} "
                            f"via {nei}, protects against node {nh}: "
                            f"{n_d_path}"
                        )

        return lfas

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
