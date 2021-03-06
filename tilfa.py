
import networkx as nx
import os
from diagram import diagram
from spf import spf


class tilfa:
    """This class provides draft-ietf-rtgwg-segment-routing-ti-lfa TI-LFA calculations"""

    def __init__(self, debug=0, ep_space=True, trombone=False):
        """
        Init the TI-LFA class.

        :param int debug: debug level, 0 is disabled.
        :param bool ep_space: Consider nodes in EP space not just P-space
        ####:param bool trombone: Allow pq_node>dst path to trombone through p_node
        :return None: __init__ shouldn't return anything
        :rtype: None
        """
        self.debug = 0
        self.diagram = diagram(debug=2)
        self.ep_space = ep_space
        self.path_types = ["tilfas_link", "tilfas_node"]
        self.spf = spf(debug=self.debug)
        ###self.trombone = trombone

    def check_sids(self, graph):
        """
        Check that each node has a node SID and that each adjacency has an 
        adjacency SID, and they they are valid and unique.

        :param networkx.Graph graph: NetworkX graph object
        :return bool True: True if all SIDs are present and unique, else false
        :rtype: bool
        """

        node_sids = []
        for node in graph.nodes():
            if "node_sid" not in graph.nodes[node]:
                raise Exception(
                    f"Node {node} is missing a node SID, can't run TI-LFA"
                )
            if type(graph.nodes[node]["node_sid"]) != int:
                raise Exception(
                    f"Node {node} node SID is not an int, can't run TI-LFA"
                )
            node_sids.append(graph.nodes[node]["node_sid"])

        if len(set(node_sids)) < len(node_sids):
            raise Exception(
                "Nodes found with non-unique node SIDs: "
                f"{[sid for sid in node_sids if node_sids.count(sid) > 1]}"
            )

        adj_sids = []
        for edge in graph.edges():
            if "adj_sid" not in graph.edges[edge]:
                raise Exception(
                    f"Link {edge} is missing an adjacency SID, can't run TI-LFA"
                )
            if type(graph.edges[edge]["adj_sid"]) != int:
                raise Exception(
                    f"Link {edge} adjacency SID is not an int, can't run TI-LFA"
                )
            adj_sids.append(graph.edges[edge]["adj_sid"])

        if len(set(adj_sids)) < len(adj_sids):
            raise Exception(
                "Links found with non-unique adjacency SIDs: "
                f"{[sid for sid in adj_sids if adj_sids.count(sid) > 1]}"
            )

    def draw(self, graph, outdir, topology):
        """
        Loop over the generated topologies and render them as diagram files.

        :param networkx.Graph graph: NetworkX graph object
        :param str outdir: String of the root output directory path
        :param dict topology: Topology paths dict
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

                if len(topology[src][dst][path_type]) < 1:
                    continue

                tilfa_graph = graph.copy()

                # Highlight the failed first-hop link as red
                for path in topology[src][dst]["spf_metric"]:
                    tilfa_graph = self.diagram.highlight_fh_link(
                        "red",
                        tilfa_graph,
                        path,
                    )

                # Highlight the failed first-hop node(s) as red
                if path_type == "tilfas_node":
                    for path in topology[src][dst]["spf_metric"]:
                        tilfa_graph = self.diagram.highlight_fh_node(
                            "red",
                            tilfa_graph,
                            path,
                        )

                for tilfa in topology[src][dst][path_type]:
                    # Highlight the path(s) from src to the PQ node(s)
                    for s_p_path in tilfa[0]:
                        print(f"s_p_path: {s_p_path}")
                        tilfa_graph = self.diagram.highlight_links(
                            "purple", tilfa_graph, s_p_path
                        )
                        tilfa_graph = self.diagram.highlight_nodes(
                            "purple", tilfa_graph, s_p_path
                        )
                    # Highlight the path(s) from the PQ node(s) to dst
                    for q_d_path in tilfa[1]:
                        print(f"q_d_path: {q_d_path}")
                        tilfa_graph = self.diagram.highlight_links(
                            "green", tilfa_graph, q_d_path
                        )
                        tilfa_graph = self.diagram.highlight_nodes(
                            "green", tilfa_graph, q_d_path
                        )

                tilfa_graph = self.diagram.highlight_src_dst(
                    "lightblue", dst, tilfa_graph, src
                )
                # Add labels to links showing their cost
                tilfa_graph = self.diagram.label_link_weights(tilfa_graph)
                tilfa_graph = self.diagram.label_link_add_adjsid(tilfa_graph)
                tilfa_graph = self.diagram.label_node_id(tilfa_graph)
                tilfa_graph = self.diagram.label_node_add_nodesid(tilfa_graph)

                self.diagram.gen_diagram(
                    (src + "_" + dst + "_" + path_type),
                    tilfa_graph,
                    os.path.join(outdir, src, path_type),
                )

    def gen_ep_space(self, dst, f_type, graph, src):
        """
        Return a list of nodes in src's Extended P-space which avoid resource X

        :param str dst: Dst node in "graph" to calculate EP-space not via X
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node in "graph" to calculate EP-space from
        :return ep_space: List of nodes in src's EP-space with respect to X
        :rtype: list
        """

        """
        TI-LFA Text:
        The Extended P-space P'(R,X) of a node R w.r.t. a resource X is the
        set of nodes that are reachable from R or a neighbor of R, without
        passing through X.
        """

        if f_type == "link":
            ep_space = self.gen_link_p_space(dst, graph, src)
        elif f_type == "node":
            ep_space = self.gen_node_p_space(dst, graph, src)
        else:
            raise Exception(f"Unrecognised EP-space type {f_type}")

        for nei in graph.neighbors(src):
            if nei == dst:
                continue

            if f_type == "link":
                n_p_space = self.gen_link_p_space(dst, graph, nei)
            elif f_type == "node":
                n_p_space = self.gen_node_p_space(dst, graph, nei)
            else:
                raise Exception(f"Unrecognised EP-space type {f_type}")

            if src in n_p_space:
                n_p_space.remove(src)

            for ep_node in n_p_space:
                """
                Skip EP-nodes which have the pre-failure first-hop link(s) from src
                to dst in the pre-failure path(s) from src to EP-node:
                """
                s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
                s_d_fh_links = [(path[0], path[1]) for path in s_d_paths]

                s_ep_paths = self.spf.gen_metric_paths(
                    dst=ep_node, graph=graph, src=src
                )
                s_ep_links = [
                    (path[idx], path[idx + 1])
                    for path in s_ep_paths
                    for idx in range(0, len(path) - 1)
                ]
                
                overlap = [
                    link for link in s_ep_links if link in s_d_fh_links
                ]
                if overlap:
                    if self.debug > 1:
                        print(
                            f"Skipping link EP-space node {ep_node} due "
                            f"to overlap:\n"
                            f"{s_ep_links},{ep_node}\n"
                            f"{s_d_fh_links},{dst}"
                        )
                    continue

                if ep_node not in ep_space:
                    ep_space.append(ep_node)

        return ep_space

    def gen_link_p_space(self, dst, graph, src):
        """
        Return a list of nodes in src's P-space relevant to the first-hop
        link(s) towards dst.

        :param str dst: Node in "graph" to calculate P-space to, avoiding S-F
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node in "graph" which must avoid S-F link to Dst
        :return p_space: List of nodes in src's P-space with respect to S-F
        :rtype: list
        """

        """
        TI-LFA Text:
        The P-space P(R,X) of a node R w.r.t. a resource X (e.g. a link S-F,
        a node F, or a SRLG) is the set of nodes that are reachable from R
        without passing through X. It is the set of nodes that are not
        downstream of X in SPT_old(R).
        """

        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        s_d_fh_links = [(path[0], path[1]) for path in s_d_paths]

        if self.debug > 1:
            print(
                f"Checking for link protecting P-nodes of {src} not via "
                f"link(s): {s_d_fh_links}"
            )

        p_space = []
        for p_node in graph.nodes:

            if p_node == src or p_node == dst:
                continue

            s_p_paths = self.spf.gen_metric_paths(
                dst=p_node, graph=graph, src=src
            )

            """
            Skip P-nodes which have the pre-failure first-hop link(s) from src
            to dst in the pre-failure path(s) from src to P-node:
            """
            s_p_links = [
                (path[idx], path[idx + 1])
                for path in s_p_paths
                for idx in range(0, len(path) - 1)
            ]
            overlap = [
                link for link in s_p_links if link in s_d_fh_links
            ]
            if overlap:
                if self.debug > 1:
                    print(
                        f"Skipping link protecting P-space node {p_node} due "
                        f"to overlap:\n"
                        f"{s_p_links},{p_node}\n"
                        f"{s_d_fh_links},{dst}"
                    )
                continue

            p_space.append(p_node)

        return p_space

    def gen_link_pq_space(self, dst, graph, link_q_space, src):
        """
        Return the list of Q-space nodes which are link protecting against S-F
        from S to D.

        :param str dst: Destination node name in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param list link_q_space: List of Q-space nodes in "graph" relative to
        D not via S-F
        :param str src: Source node name in "graph"
        :return link_pq_nodes: List of nodes in D's Q-space and in post-SPF
        :rtype: list
        """

        """
        TI-LFA Text:
        4.2. Q-Space property computation for a link S-F, over post-convergence
        paths

        We want to determine which nodes on the post-convergence path from
        the PLR to the destination D are in the Q-Space of destination D
        w.r.t. link S-F.

        This can be found by intersecting the post-convergence path to D,
        assuming the failure of S-F, with Q(D, S-F).
        """

        link_pq_space = []

        # Get the pre-converge path(s) to D
        pre_s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        pre_s_d_fh_links = [(src, path[1]) for path in pre_s_d_paths]

        # Remove the pre-convergence first-hop link(s) from the graph
        tmp_g = graph.copy()
        for fh_link in pre_s_d_fh_links:
            tmp_g.remove_edge(*fh_link)

        # Re-calculate the path(s) to D in the failure state (post-convergence)
        post_s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=tmp_g, src=src)
        for post_s_d_path in post_s_d_paths:
            for q_node in link_q_space: # Q-space doesn't include src or dst
                if q_node in post_s_d_path:
                    link_pq_space.append(q_node)

        return link_pq_space

    def gen_link_q_space(self, dst, graph, src):
        """
        Return a list of nodes in dst's Q-space which avoid link(s) S-F.

        :param str dst: Dest node in "graph" to calculate Q-space for
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node in "graph" relevant to S-F link
        :return q_space: List of nodes in dst's Q-space with respect to S-F
        :rtype: list
        """

        """
        TI-LFA Text:
        The Q-Space Q(D,X) of a destination node D w.r.t. a resource X is the
        set of nodes which do not use X to reach D in the initial state of
        the network. In other words, it is the set of nodes which have D in
        their P-space w.r.t. S-F, F, or a set of links adjacent to S).
        """

        q_space = []

        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        s_d_fh_links = [(src, path[1]) for path in s_d_paths]

        for q_node in graph.nodes:

            if q_node == src or q_node == dst:
                continue

            q_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=q_node)

            """
            Skip Q-nodes which have the pre-failure first-hop link(s) from src
            to dst in the pre-failure path(s) from P-node to dst:
            """
            q_d_links = [
                (path[idx], path[idx + 1])
                for path in q_d_paths
                for idx in range(0, len(path) - 1)
            ]
            overlap = [
                link for link in q_d_links if link in s_d_fh_links
            ]
            if overlap:
                if self.debug > 1:
                    print(
                        f"Skipping link protecting Q-space node {q_node} due "
                        f"to overlap:\n"
                        f"{q_d_links}\n"
                        f"{s_d_fh_links}"
                    )
                continue

            q_space.append(q_node)

        return q_space

    def gen_metric_link_tilfas(self, dst, graph, link_ep_space, link_pq_space, link_q_space, src):
        """
        Return all link protecting TI-LFAs paths from src to dst.
        Do this by returning all equal-cost explicit paths (based on metric,
        not hop count) between "src" and "dst" nodes in "graph" that satisfy
        the rules below.

        :param str dst: Destination node name in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param list link_ep_space: EP- or P-space of Src node
        :param list link_q_space: List of nodes in D's Q-space
        :param list link_pq_space: List of nodes in D's Q-Space in post-SPF
        :param str src: Source node name in "graph"
        :return tilfa_paths: list of dict of TI-LFA paths 
        :rtype: list
        """

        tilfa_paths = []
        lfa_cost = 0
        lfa_p_cost = 0

        """
        TI-LFA Text:
        5.1. FRR path using a direct neighbor
        When a direct neighbor is in P(S,X) and Q(D,x) and on the post-
        convergence path, the outgoing interface is set to that neighbor and
        the repair segment list MUST be empty.

        This is comparable to a post-convergence LFA FRR repair.
        """
        for nei in graph.neighbors(src):
            if nei in link_pq_space:

                """                
                Check that the neighbour/pq-node isn't reached via the same
                failed fist hop link(s) toward dst:
                """
                pre_s_pq_paths = self.spf.gen_metric_paths(dst=nei, graph=graph, src=src)
                pre_s_pq_fh_links = [(src, path[1]) for path in pre_s_pq_paths]

                pre_s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
                pre_s_d_fh_links = [(src, path[1]) for path in pre_s_d_paths]
                
                overlap = [
                    fh_link for fh_link in pre_s_d_fh_links if fh_link in pre_s_pq_fh_links
                ]
                if overlap:
                    if self.debug > 1:
                        print(
                            f"Skipping directly connected neighbour {nei} due "
                            f"to overlap:\n"
                            f"{pre_s_pq_fh_links},{nei}\n"
                            f"{pre_s_d_fh_links},{dst}"
                        )
                    continue
                if self.debug > 1:
                    print(
                        f"Directly connected neighbour {nei} is link "
                        f"protecting from {src} to {dst}"
                    )

                n_d_paths = self.spf.gen_metric_paths(
                    dst=dst, graph=graph, src=nei
                )
                cost = self.spf.gen_path_cost(graph, [src] + n_d_paths[0])
                if cost < lfa_cost or lfa_cost == 0:
                    lfa_cost = cost
                    tilfa_paths = [
                        (
                            [[src, nei]],
                            n_d_paths,
                            [[]]
                        )
                    ]
                    if self.debug > 0:
                        print(f"TI-LFA 5.1.1: {tilfa_paths}")
                elif cost == lfa_cost:
                    tilfa_paths.append(
                            ([[src, nei]], [n_d_path for n_d_path in n_d_paths], [[]])
                        )
                    if self.debug > 0:
                        print(f"TI-LFA 5.1.2: {tilfa_paths}")

        """
        TI-LFA Text:
        5.2. FRR path using a PQ node
        When a remote node R is in P(S,X) and Q(D,x) and on the post-
        convergence path, the repair list MUST be made of a single node
        segment to R and the outgoing interface MUST be set to the outgoing
        interface used to reach R.

        This is comparable to a post-convergence RLFA repair tunnel.
        """
        for p_node in graph.nodes:
            if p_node == src or p_node == dst:
                continue
            if p_node not in graph.neighbors(src):
                if p_node in link_pq_space:
                    if self.debug > 1:
                        print(
                            f"Remote P-node {p_node} is link protecting from "
                            f"from {src} to {dst}"
                        )

                    # Get the pre-converge path(s) to D
                    pre_s_p_paths = self.spf.gen_metric_paths(dst=p_node, graph=graph, src=src)
                    pre_s_p_fh_links = [(src, path[1]) for path in pre_s_p_paths]
                    
                    # Remove the pre-convergence the first-hop link(s) from the graph
                    tmp_g = graph.copy()
                    for fh_link in pre_s_p_fh_links:
                        tmp_g.remove_edge(*fh_link)
                    
                    # Re-calculate the path(s) to D in the failure state (post-convergence)
                    post_s_p_paths = self.spf.gen_metric_paths(dst=p_node, graph=tmp_g, src=src)

                    p_d_paths = self.spf.gen_metric_paths(
                        dst=dst, graph=tmp_g, src=p_node
                    )

                    """
                    Check if this path has a lower cost from src to dst
                    than the current TI-LFA path(s)
                    """
                    cost = self.spf.gen_path_cost(tmp_g, post_s_p_paths[0] + p_d_paths[0][1:])
                    if cost < lfa_cost or lfa_cost == 0:
                        lfa_cost = cost
                        tilfa_paths = [
                            (
                                post_s_p_paths,
                                p_d_paths,
                                [graph.nodes[p_node]["node_sid"]]
                            )
                        ]
                        if self.debug > 0:
                            print(f"TI-LFA 5.2.1: {tilfa_paths}")

                    # If it has the same cost...
                    elif cost == lfa_cost:
                        """
                        Check if this path is the same as an existing TI-LFA,
                        but using a different repair node along the same path.
                        Prefer scenario 1 over scenario 2...
                        Scenario 1: [ src -> R1 ] + [ R2 -> R3 -> dst ]
                        Scenario 2: [ src -> R1 -> R2 ] + [ R3 -> dst ]
                        This hopefully reduces the required segment stack and
                        thus reduces the MTU required and likelihood for
                        excessive MPLS label push operations.
                        """
                        for tilfa in tilfa_paths:
                            if tilfa[0][-1] != post_s_p_paths[0][-1]:
                                cost = self.spf.gen_path_cost(tmp_g, post_s_p_paths[0])
                                this_lfa = self.spf.gen_path_cost(tmp_g, tilfa[0][0]) ########## Can any of the paths to p_node be different cost?
                                if cost < this_lfa:
                                    tilfa_paths = [
                                        (
                                            post_s_p_paths,
                                            p_d_paths,
                                            [graph.nodes[p_node]["node_sid"]]
                                        )
                                    ]
                                    if self.debug > 0:
                                        print(f"TI-LFA 5.2.2: {tilfa_paths}")
                                    break
                        
                        # Else it's an ECMP path with the same cost to p_node
                        else:
                            tilfa_paths.append (
                                (
                                    post_s_p_paths,
                                    p_d_paths,
                                    [graph.nodes[p_node]["node_sid"]]
                                )
                            )
                            if self.debug > 0:
                                print(f"TI-LFA 5.2.3: {tilfa_paths}")

        """
        TI-LFA Text:
        5.3. FRR path using a P node and Q node that are adjacent

        When a node P is in P(S,X) and a node Q is in Q(D,x) and both are on
        the post-convergence path and both are adjacent to each other, the
        repair list MUST be made of two segments: A node segment to P (to be
        processed first), followed by an adjacency segment from P to Q.

        This is comparable to a post-convergence DLFA repair tunnel.
        """
        for p_node in graph.nodes:
            if p_node == src or p_node == dst:
                continue
            if p_node in link_ep_space:
                if p_node not in link_pq_space:
                    for q_node in graph.neighbors(p_node):
                        if q_node == src or q_node == dst:
                            continue
                        if q_node in link_q_space:
                            if self.debug > 1:
                                print(
                                    f"P-Node {p_node} is neighbour of "
                                    f"{q_node}, which together are link "
                                    f"protecting from {src} to {dst}"
                                )
                            s_p_paths = self.spf.gen_metric_paths(
                                dst=p_node, graph=graph, src=src
                            )
                            q_d_paths = self.spf.gen_metric_paths(
                                dst=dst, graph=graph, src=q_node
                            )

                            cost = self.spf.gen_path_cost(
                                graph, [s_p_paths[0] + q_d_paths[0][1:]]
                            )
                            if cost < lfa_cost or lfa_cost == 0:
                                lfa_cost = cost
                                tilfa_paths = [
                                    (
                                        [s_p_path + [q_node] for s_p_path in s_p_paths],
                                        q_d_paths,
                                        [
                                            graph.nodes[p_node]["node_sid"],
                                            graph.edges[(p_node, q_node)]["adj_sid"]
                                        ]
                                    )
                                ]
                                if self.debug > 0:
                                    print(f"TI-LFA 5.3.1: {tilfa_paths}")
                            elif cost == lfa_cost:
                                tilfa_paths.append(
                                    (
                                        [s_p_path + [q_node] for s_p_path in s_p_paths],
                                        q_d_paths,
                                        [
                                            graph.nodes[p_node]["node_sid"],
                                            graph.edges[(p_node, q_node)]["adj_sid"]
                                        ]
                                    )
                                )
                                if self.debug > 0:
                                    print(f"TI-LFA 5.3.2: {tilfa_paths}")

        """
        5.4. Connecting distant P and Q nodes along post-convergence paths

        In some cases, there is no adjacent P and Q node along the post-
        convergence path. However, the PLR can perform additional
        computations to compute a list of segments that represent a loop-free
        path from P to Q. How these computations are done is out of scope of
        this document.

        ---

        Thanks you bastards. We shall calculate any P to Q paths. If some
        exist, calculate the Source to P paths, then append them together.
        """

        # Get the pre-converge path(s) to D
        pre_s_p_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        pre_s_p_fh_links = [(src, path[1]) for path in pre_s_p_paths]
        
        # Remove the pre-convergence the first-hop link(s) from the graph
        tmp_g = graph.copy()
        for fh_link in pre_s_p_fh_links:
            tmp_g.remove_edge(*fh_link)

        """
        For each ep node calculate the post convergence path to each pq node.
        Build a list of all these paths to get the lowest cost one.
        """
        ep_nodes = [node for node in link_ep_space if node not in link_pq_space]
        pq_nodes = [node for node in link_pq_space if node not in link_ep_space]
        p_q_paths = []
        p_q_cost = 0
        for ep in ep_nodes:
            for pq in pq_nodes:
                post_p_q_paths = self.spf.gen_metric_paths(dst=pq, graph=tmp_g, src=ep)

                if len(post_p_q_paths[0]) > 0:
                    for path in post_p_q_paths:
                        cost = self.spf.gen_path_cost(tmp_g, path)
                        if cost < p_q_cost or p_q_cost == 0:
                            p_q_paths = [path]
                            p_q_cost = cost
                        elif cost == p_q_cost:
                            if path not in p_q_paths:
                                p_q_paths.append(path)

        if p_q_paths:
            # If we found p to q paths, append them to s to p paths
            s_q_paths = []
            for p_q_path in p_q_paths:
                p = p_q_path[0]
                s_p_paths = self.spf.gen_metric_paths(dst=p, graph=tmp_g, src=src)
                for s_p_path in s_p_paths:
                    s_q_paths.append(s_p_path + p_q_path[1:])

            for s_q_path in s_q_paths:
                cost = self.spf.gen_path_cost(tmp_g, s_q_path)

                if cost < lfa_cost or lfa_cost == 0:
                    if self.debug > 1:
                        print(
                            f"Remote P & Q nodes in {s_q_path} are link "
                            f"protecting from {src} to {dst}"
                        )
                    q = s_q_path[-1]
                    q_d_paths = self.spf.gen_metric_paths(dst=dst, graph=tmp_g, src=q)
                    lfa_cost = cost
                    tilfa_paths = [
                        (
                            [s_q_path],
                            q_d_paths,
                            [
                                self.paths_adj_sids(tmp_g, [s_q_path])
                            ]
                        )
                    ]
                    if self.debug > 0:
                        print(f"TI-LFA 5.4.1: {tilfa_paths}")

                elif cost == lfa_cost:
                    if self.debug > 1:
                        print(
                            f"Remote P & Q nodes in {s_q_path} are link "
                            f"protecting from {src} to {dst}"
                        )
                    q = s_q_path[-1]
                    q_d_paths = self.spf.gen_metric_paths(dst=dst, graph=tmp_g, src=q)
                    tilfa_paths.append(
                        (
                            [s_q_path],
                            q_d_paths,
                            [
                                self.paths_adj_sids(tmp_g, [s_q_path])
                            ]
                        )
                    )
                    if self.debug > 0:
                        print(f"TI-LFA 5.4.2: {tilfa_paths}")

        return tilfa_paths

    def gen_metric_node_tilfas(self, dst, graph, node_ep_space, node_pq_space, src):
        """
        Return all node protecting rLFAs.
        Do this by filtering the list of link rLFAs "tilfas_link" for those
        with pre-convergence best path(s) from all repair tunnel end-points
        {p}, which don't pass through any of the first-hops of any of the
        pre-convergence best-paths from src to dst.

        :param str dst: Destination node name in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param list tilfas_link: list of link protecting rLFA paths in "graph"
        :param str src: Source node name in "graph"
        :return tilfas_node: List of tuples of equal-cost node protecting TI-LFAs to dst
        :rtype: list
        """

        tilfas_node = []

        return tilfas_node

    def gen_metric_paths(self, dst, graph, src):
        """
        Return all TI-LFA paths between the "src" and "dst" nodes in "graph",
        based on link metric (not hop count), which provide link and node
        protection. Returned are all TI-LFA paths in a dict, keyed by type (link
        or node), the key values are lists of tuples containing the path to
        the P node and path from P to D.

        :param str dst: Destination node name in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node name in "graph"
        :return tilfa_paths: Dict with list(s) of tuples
        :rtype: list
        """

        tilfas = {}
        if self.debug > 0:
            print(f"Calculating TI-LFA paths from {src} to {dst}")

        tilfas = {
            "tilfas_link": [],
            "tilfas_node": []
        }

        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        # There are no paths between this src,dst pair
        if not s_d_paths:
            return tilfas

        """
        TI-LFA Text:
        5. TI-LFA Repair path
        The TI-LFA repair path (RP) consists of an outgoing interface and a
        list of segments (repair list (RL)) to insert on the SR header.  The
        repair list encodes the explicit post-convergence path to the
        destination, which avoids the protected resource X and, at the same
        time, is guaranteed to be loop-free irrespective of the state of FIBs
        along the nodes belonging to the explicit path. 

        The TI-LFA repair path is found by intersecting P(S,X) and Q(D,X)
        with the post-convergence path to D and computing the explicit SR-
        based path EP(P, Q) from P to Q when these nodes are not adjacent
        along the post convergence path.  The TI-LFA repair list is expressed
        generally as (Node_SID(P), EP(P, Q)).
        """
        
        if self.ep_space:
            link_ep_space = self.gen_ep_space(dst, "link", graph, src)
            node_ep_space = self.gen_ep_space(dst, "node", graph, src)
            if self.debug > 0:
                print(f"link_ep_space: {link_ep_space}")
                print(f"node_ep_space: {node_ep_space}")
        else:
            link_p_space = self.gen_link_p_space(dst, graph, src)
            node_p_space = self.gen_node_p_space(dst, graph, src)
            if self.debug > 0:
                print(f"link_p_space: {link_p_space}")
                print(f"node_p_space: {node_p_space}")
        
        link_q_space = self.gen_link_q_space(dst, graph, src)
        node_q_space = self.gen_node_q_space(dst, graph, src)
        if self.debug > 0:
            print(f"link_q_space: {link_q_space}")
            print(f"node_q_space: {node_q_space}")

        link_pq_space = self.gen_link_pq_space(dst, graph, link_q_space, src)
        node_pq_space = self.gen_node_pq_space(dst, graph, node_q_space, src)
        if self.debug > 0:
            print(f"link_pq_space: {link_pq_space}")
            print(f"node_pq_space: {node_pq_space}")


        if self.ep_space:
            link_tilfas = self.gen_metric_link_tilfas(dst, graph, link_ep_space, link_pq_space, link_q_space, src)
        else:
            link_tilfas = self.gen_metric_link_tilfas(dst, graph, link_p_space, link_pq_space, link_q_space, src)
        if self.debug > 0:
            print(f"link_tilfas: {link_tilfas}")
        tilfas["tilfas_link"] = link_tilfas

        return tilfas
        ############################

        if self.ep_space:
            node_tilfas = self.gen_metric_node_tilfas(dst, graph, node_ep_space, node_pq_space, src)
        else:
            node_tilfas = self.gen_metric_node_tilfas(dst, graph, node_p_space, node_pq_space, src)
        if self.debug > 0:
            print(f"node_tilfas: {node_tilfas}")
        tilfas["tilfas_node"] = node_tilfas

        return tilfas

    def gen_node_p_space(self, dst, graph, src):
        """
        Return a list of nodes in src's P-space relevant to the first-hop
        nodes(s) towards dst.

        :param str dst: Node in "graph" to calculate P-space to, avoiding F
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node in "graph" which must avoid F node to Dst
        :return p_space: List of nodes in src's P-space with respect to F
        :rtype: list
        """

        """
        TI-LFA Text:
        The P-space P(R,X) of a node R w.r.t. a resource X (e.g. a link S-F,
        a node F, or a SRLG) is the set of nodes that are reachable from R
        without passing through X. It is the set of nodes that are not
        downstream of X in SPT_old(R).
        """

        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        s_d_fhs = [path[1] for path in s_d_paths]

        if self.debug > 1:
            print(
                f"Checking for node protecting P-space nodes of {src} not via "
                f"first-hop(s): {s_d_fhs}"
            )

        p_space = []
        for p_node in graph.nodes:

            # Exclude nodes which are a first-hop towards dst:
            if p_node == src or p_node == dst:
                continue

            if p_node in s_d_fhs:
                if self.debug > 1:
                    print(
                        f"Skipping node protecting P-space node {p_node} "
                        f"because it is a first-hop(s) towards {dst}: "
                        f"{s_d_fhs}"
                    )
                continue

            s_p_paths = self.spf.gen_metric_paths(
                dst=p_node, graph=graph, src=src
            )

            """
            Check if any of the p_node->dst path(s) contain any of the
            first-hop(s) from src->dst, those are the nodes we want to avoid.
            """
            overlap = [
                fh for fh in s_d_fhs for s_p_path in s_p_paths if fh in s_p_path
            ]
            if overlap:
                if self.debug > 1:
                    print(
                        f"Skipping node protecting P-space node {p_node}, "
                        f"path(s) from {src} to {p_node} overlap with "
                        f"first-hop(s) in path(s) from {src} to {dst}: "
                        f"{s_p_paths}"
                    )
                continue

            p_space.append(p_node)

        return p_space

    def gen_node_pq_space(self, dst, graph, node_q_space, src):
        """
        Return the list of Q-space nodes which are node protecting against F
        from S to D.

        :param str dst: Destination node name in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param list node_q_space: List of Q-space nodes in "graph" relative to
        D not via F
        :param str src: Source node name in "graph"
        :return node_pq_space: List of nodes in D's Q-space and in post-SPF
        :rtype: list
        """

        """
        TI-LFA Text:
        4.4. Q-Space property computation for a node F, over post-convergence
        paths

        We want to determine which nodes on the post-convergence from the PLR
        to the destination D are in the Q-Space of destination D w.r.t. node
        F.

        This can be found by intersecting the post-convergence path to D,
        assuming the failure of F, with Q(D, F).
        """

        node_pq_space = []

        # Get the pre-converge path(s) to D and remove the first-hop node(s)
        pre_s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        pre_s_d_fh_nodes = [path[1] for path in pre_s_d_paths]

        # There are no node protecting paths for a directly connected neighbour
        for fh_node in pre_s_d_fh_nodes:
            if fh_node in graph.neighbors(src):
                return node_pq_space

        tmp_g = graph.copy()
        for fh_node in pre_s_d_fh_nodes:
            tmp_g.remove_node(fh_node)

        # Recalculate the path(s) to D in the failure state (post-convergence)
        post_s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=tmp_g, src=src)

        for post_s_d_path in post_s_d_paths:
            for q_node in node_q_space:
                if q_node in post_s_d_path:
                    node_pq_space.append(q_node)

        return node_pq_space

    def gen_node_q_space(self, dst, graph, src):
        """
        Return a list of nodes in dst's Q-space which avoid node(s) F.

        :param str dst: Dest node in "graph" to calculate Q-space for
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node in "graph" relevant to F node
        :return q_space: List of nodes in dst's Q-space with respect to F
        :rtype: list
        """

        """
        TI-LFA Text:
        The Q-Space Q(D,X) of a destination node D w.r.t. a resource X is the
        set of nodes which do not use X to reach D in the initial state of
        the network. In other words, it is the set of nodes which have D in
        their P-space w.r.t. S-F, F, or a set of links adjacent to S).
        """

        q_space = []

        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        s_d_fhs = [path[1] for path in s_d_paths]

        for q_node in graph.nodes:

            if q_node == src or q_node == dst:
                continue

            q_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=q_node)

            overlap = [
                s_d_fh for s_d_fh in s_d_fhs for q_d_path in q_d_paths if s_d_fh in q_d_path
            ]

            if overlap:
                if self.debug > 1:
                    print(
                        f"Skipping node protecting Q-Space node {q_node}, "
                        f"path to {dst} overlaps with hop(s) in path(s) from "
                        f"{src} toward {dst}: {q_d_paths}"
                    )
                continue

            q_space.append(q_node)

        return q_space

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

    def paths_adj_sids(self, graph, paths):
        """
        Return lists of adj SIDs that will steer along the explicit path

        :param networkx.Graph graph: NetworkX graph object
        :param list paths: List of list of nodes that form the explicit path(s)
        :return adj_sids: List of adj SIDs along path
        :rtype: list of lists
        """
        adj_sids = []
        for path in paths:
            sids = []
            for idx, node in enumerate(path):
                if idx < (len(path) - 1):
                    sids.append(graph.edges[(node, path[idx + 1])]["adj_sid"])
            adj_sids.append(sids)

        if self.debug > 1:
            print(f"path_adj_sids: {adj_sids}")

        return adj_sids
