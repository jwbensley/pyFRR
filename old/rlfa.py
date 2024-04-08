import networkx as nx
import os
from diagram import diagram
from spf import spf


class rlfa:
    """This class provides RFC7490 rLFA calculations"""

    def __init__(self, debug=0, ep_space=True, trombone=False):
        """
        Init the rLFA class.

        :param int debug: Debug level, 0 is disabled.
        :param bool ep_space: Consider nodes in EP space not just P-space
        :param bool trombone: Allow pq_node>dst path to trombone through p_node
        :return None: __init__ shouldn't return anything
        :rtype: None
        """
        self.debug = debug
        self.diagram = diagram(debug=self.debug)
        self.ep_space = ep_space
        self.path_types = ["rlfas_link", "rlfas_node"]
        self.spf = spf(debug=self.debug)
        self.trombone = trombone

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

                if len(topology[src][dst][path_type]) > 0:
                    frr_graph = graph.copy()

                    # Highlight the failed first-hop link(s) as red
                    for path in topology[src][dst]["spf_metric"]:
                        frr_graph = self.diagram.highlight_fh_link(
                            "red",
                            frr_graph,
                            path,
                        )

                    # Highlight the failed first-hop node(s) as red
                    if path_type == "rlfas_node":
                        for path in topology[src][dst]["spf_metric"]:
                            frr_graph = self.diagram.highlight_fh_node(
                                "red",
                                frr_graph,
                                path,
                            )

                    for rlfa in topology[src][dst][path_type]:
                        # Highlight the path(s) from src to the PQ node(s)
                        for s_pq_path in rlfa[0]:
                            frr_graph = self.diagram.highlight_links(
                                "purple", frr_graph, s_pq_path
                            )
                            frr_graph = self.diagram.highlight_nodes(
                                "purple", frr_graph, s_pq_path
                            )
                        # Highlight the path(s) from the PQ node(s) to dst
                        for pq_d_path in rlfa[1]:
                            frr_graph = self.diagram.highlight_links(
                                "green", frr_graph, pq_d_path
                            )
                            frr_graph = self.diagram.highlight_nodes(
                                "green", frr_graph, pq_d_path
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

    def gen_ep_space(self, dst, graph, src):
        """
        Return a list of nodes in src's Extended P-space.

        :param str dst: Dest node in "graph" to calculate EP-space (S-E link)
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node in "graph" to calculate EP-space (S-E link)
        :return ep_space: List of nodes in src's EP-space with respect to S-E
        :rtype: list
        """

        """
        RFC7490:
        Extended P-space
        Router S's extended P-space is the union of the P-spaces of each of S's
        neighbors (N). This may be calculated by computing an SPT at each of
        S's neighbors (excluding E) and excising the subtree reached via the
        path N->S->E.  Note this will excise those routers that are reachable
        through all ECMPs that include link S-E.
        ...
        In cost terms, a router (P) is in extended P-space if the shortest path
        cost N->P is strictly less than the shortest path cost N->S->E->P. 
        In other words, once the packet is forced to N by S, it is a lower cost
        for it to continue on to P by any path except one that takes it back to
        S and then across the S->E link.
        """

        ep_space = []
        for nei in graph.neighbors(src):
            if nei == dst:
                continue

            nei_p_space = self.gen_p_space(dst, graph, nei, src)
            for p in nei_p_space:
                if p == src:
                    continue

                n_p_cost = self.spf.gen_metric_cost(
                    dst=p, graph=graph, src=nei
                )
                n_s_cost = self.spf.gen_metric_cost(
                    dst=src, graph=graph, src=nei
                )
                s_d_cost = self.spf.gen_metric_cost(
                    dst=dst, graph=graph, src=src
                )
                d_p_cost = self.spf.gen_metric_cost(
                    dst=p, graph=graph, src=dst
                )

                if self.debug > 1:
                    print(
                        f"ep-space {nei}: {n_p_cost} < "
                        f"({n_s_cost} + {s_d_cost} + {d_p_cost})?"
                    )
                if n_p_cost < (n_s_cost + s_d_cost + d_p_cost):
                    if p not in ep_space:
                        ep_space.append(p)

        return ep_space

    def gen_metric_paths(self, dst, graph, src):
        """
        Return all rLFA paths between the "src" and "dst" nodes in "graph",
        based on link metric (not hop count), which provide link and node
        protection. Returned are all rLFA paths in a dict, keyed by type (link
        or node), the key values are lists of tuples containing the path to
        the P node and path from P to D.

        :param str dst: Destination node name in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node name in "graph"
        :return rlfas: Dict with list(s) of tuples
        :rtype: list
        """

        rlfas = {
            "rlfas_link": [],
            "rlfas_node": []
        }
        
        if self.debug > 0:
            print(f"Calculating rLFA paths from {src} to {dst}")

        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        # There are no paths between this src,dst pair
        if not s_d_paths:
            return rlfas

        if self.ep_space:
            ep_space = self.gen_ep_space(dst, graph, src)
            if self.debug > 0:
                print(f"ep_space: {ep_space}")
        else:
            p_space = self.gen_p_space(dst, graph, src, src)
            if self.debug > 0:
                print(f"p_space: {p_space}")

        q_space = self.gen_q_space(dst, graph, src)
        if self.debug > 0:
            print(f"q_space: {q_space}")

        if self.ep_space:
            pq_nodes = self.gen_pq_nodes(ep_space, q_space)
        else:
            pq_nodes = self.gen_pq_nodes(p_space, q_space)
        if self.debug > 0:
            print(f"pq_nodes: {pq_nodes}")

        rlfas_link = self.gen_metric_paths_link(dst, graph, pq_nodes, src)
        rlfas["rlfas_link"] = rlfas_link
        if self.debug > 0:
            print(f"rlfas_link: {rlfas_link}")

        rlfas_node = self.gen_metric_paths_node(dst, graph, rlfas_link, src)
        rlfas["rlfas_node"] = rlfas_node
        if self.debug > 0:
            print(f"rlfas_node: {rlfas_node}")

        return rlfas

    def gen_metric_paths_link(self, dst, graph, pq_nodes, src):
        """
        Return all link protecting rLFA paths from src to dst.
        Do this by returning all equal best paths (based on metric, not hop
        count) between "src" and "dst" nodes in "graph", which have an equal
        cost to the remote repair node (PQ). Also return the path(s) from the
        PQ node to "dst". These are joined in tuples:
        (path(s) to PQ, path(s) from PQ to dst)

        :param str dst: Destination node name in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param list pq_nodes: List of PQ nodes in "graph"
        :param str src: Source node name in "graph"
        :return rlfas_link: List of tuples of each equal cost rLFA to "dst"
        :rtype: list
        """

        rlfas_link = []
        rlfa_cost = 0

        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)

        for pq in pq_nodes:

            """
            RFC7490:
            Exclude the first-hop node(s) (E) along the best-path(s) toward dst.
            They may technically fall into pq_space but if the first-hop link
            (S-E) is down, they won't be the closet pq_nodes anymore.
            """
            if pq in [path[1] for path in s_d_paths]:
                continue

            s_pq_paths = self.spf.gen_metric_paths(
                dst=pq, graph=graph, src=src
            )
            s_pq_cost = self.spf.gen_metric_cost(dst=pq, graph=graph, src=src)

            # A new lower cost rLFA path is found:
            if s_pq_cost < rlfa_cost or rlfa_cost == 0:

                # Get the shortest path(s) from the pq node to dst
                pq_dst_paths = self.spf.gen_metric_paths(
                    dst=dst, graph=graph, src=pq
                )

                # If trumboning is disabled, check if this is a tumbone path:
                if not self.trombone:
                    skip = False
                    for s_pq_path in s_pq_paths:
                        for s_pq_hop in s_pq_path[:-1]:
                            for pq_dst_path in pq_dst_paths:
                                if s_pq_hop in pq_dst_path[1:]:
                                    if self.debug > 1:
                                        print(
                                            f"Skipping trombone link rLFA "
                                            f"{(s_pq_path,pq_dst_path)}"
                                        )
                                    skip = True
                    if skip:
                        continue

                """
                Create a tuple of the path(s) from src to pq and the path(s)
                from pq to dst
                """
                rlfas_link = [([path for path in s_pq_paths], pq_dst_paths)]
                rlfa_cost = s_pq_cost
                if self.debug > 0:
                    print(
                        f"New link rLFA cost: {rlfa_cost}, path(s): {rlfas_link}"
                    )

            # An equal cost rLFA path is found:
            elif s_pq_cost == rlfa_cost:
                pq_dst_paths = self.spf.gen_metric_paths(
                    dst=dst, graph=graph, src=pq
                )
                rlfas_link.append(([path for path in s_pq_paths], pq_dst_paths))
                if self.debug > 0:
                    print(f"Additional rLFA path found: {rlfas_link}")

        return rlfas_link

    def gen_metric_paths_node(self, dst, graph, rlfas_link, src):
        """
        Return all node protecting rLFAs.
        Do this by filtering the list of link rLFAs "rlfas_link" for those
        with pre-convergence best path(s) from all repair tunnel end-points
        {p}, which don't pass through any of the first-hops of any of the
        pre-convergence best-paths from src to dst.

        :param str dst: Destination node name in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param list rlfas_link: list of link protecting rLFA paths in "graph"
        :param str src: Source node name in "graph"
        :return rlfas_node: List of tuples of node protecting rLFAs
        :rtype: list
        """

        """
        RFC7490:
        Node Failures
        When the failure is a node failure rather than a point-to-point link
        failure, there is a danger that the rlfa repair will loop...The problem
        is that two or more of E's neighbors, each with E as the next hop to
        some destination D, may attempt to repair a packet addressed to
        destination D via the other neighbor and then E, thus causing a loop
        to form.

        Option 2 from the RFC is used here:
        2. Require that the path from the remote LFA repair target to
           destination D never passes through E (including in the ECMP
           case), i.e., only use node protecting paths in which the cost
           from the remote LFA repair target to D is strictly less than the
           cost from the remote LFA repair target to E plus the cost E to D.
        """

        rlfas_node = []
        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        s_d_fhs = [path[1] for path in s_d_paths]
        for s_pq_paths,pq_dst_paths in rlfas_link:
            overlap = [
                fh for fh in s_d_fhs for p_d_path in pq_dst_paths if fh in p_d_path
            ]
            if overlap:
                if self.debug > 1:
                    print(
                        f"rLFA path {(s_pq_paths,pq_dst_paths)} is not node "
                        f"protecting against {overlap} from {src} to {dst}"
                    )
            else:
                # If trumboning is disabled, check if this is a tumbone path:
                if not self.trombone:
                    skip = False
                    for s_pq_path in s_pq_paths:
                        for s_pq_hop in s_pq_path[:-1]:
                            for pq_dst_path in pq_dst_paths:
                                if s_pq_hop in pq_dst_path[1:]:
                                    if self.debug > 1:
                                        print(
                                            f"Skipping trombone node rLFA "
                                            f"{(s_pq_path,pq_dst_path)}"
                                        )
                                    skip = True
                    if skip:
                        continue

                rlfas_node.append((s_pq_paths,pq_dst_paths))

        return rlfas_node

    def gen_p_space(self, dst, graph, root, src):
        """
        Return a list of nodes in root's P-space relevant to the first-hop
        link(s) towards dst.
        When calculating P-space for node X, root == X, src == X.
        When calculating X's EP-space, root == neighbour of X, src == X.

        :param str dst: Node in "graph" to calculate P-space to, avoiding S-E
        :param networkx.Graph graph: NetworkX graph object
        :param str root: Root node in "graph" to calcuate P-space from
        :param str src: Source node in "graph" which must avoid S-E link to Dst
        :return p_space: List of nodes in root's P-space with respect to S-E
        :rtype: list
        """

        """
        RFC7490:
        P-space
        The set of routers that can be reached from S on the [PRE-CONVERGENCE!]
        shortest path tree without traversing S-E is termed the P-space of S
        with respect to the link S-E. This P-space can be obtained by computing
        a Shortest Path Tree (SPT) rooted at S and excising the subtree reached
        via the link S-E (including those routers that are members of an ECMP
        that includes link S-E).
        ...
        Expressed in cost terms, the set of routers {P} are those for which
        the shortest path cost S->P is strictly less than the shortest path
        cost S->E->P.
        """

        p_space = []


        """
        Find the cost of the lowest cost first-hop from all the best paths
        towards dst, and build a list of all first-hops toward dst. When ECMP
        is used in the pre-convergence state, the rLFA remote tunnel endpoint
        (p) must not be a first-hop along another of the ECMP paths.
        """
        r_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=root)
        fh_cost = 0
        fh_nodes = []
        for path in r_d_paths:
            cost = graph.edges[path[0], path[1]]["weight"]
            if fh_cost == 0:
                fh_cost = cost
            elif cost < fh_cost:
                fh_cost = cost
            fh_nodes.append(path[1])

        r_p_costs = {}
        fh_p_costs = {}
        for p in graph.nodes:

            if p == dst or p == root:
                continue

            """
            RFC7490:
            ...excising the subtree reached via the link S-E (including those
            routers that are members of an ECMP that includes link S-E).
            """
            p_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=p)
            if src in [src for path in p_d_paths if src in path[1:]]:
                if self.debug > 1:
                    print(
                        f"Skipping node {p} with {src} in it's best path(s) "
                        f"toward {dst}: {p_d_paths}"
                    )
                continue

            r_p_costs[p] = self.spf.gen_metric_cost(
                dst=p, graph=graph, src=root
            )

            fh_p_costs[p] = []
            for fh in fh_nodes:
                fh_p_costs[p].append(
                    self.spf.gen_metric_cost(dst=p, graph=graph, src=fh)
                )

        for p in r_p_costs:
            """
            Because this function is used calcualte both the P-Space for src
            and the EP-space of src's neighbours, in the later case a neighbour
            of src may choose a P node which is via the S-E link
            """
            s_p_paths = self.spf.gen_metric_paths(dst=p, graph=graph, src=src)
            if dst in [dst for path in s_p_paths if dst in path]:
                if self.debug > 1:
                    print(
                        f"Skipping node {p} with {dst} in the best path(s) "
                        f"from {src} to {p}: {s_p_paths}"
                    )
                continue

            """
            RFC7490:
            Expressed in cost terms, the set of routers {P} are those for which
            the shortest path cost S->P is strictly less than the shortest path
            cost S->E->P.
            """
            if self.debug > 1:
                print(
                    f"p-space {p}: {r_p_costs[p]} < "
                    f"({fh_cost} + {min(fh_p_costs[p])})?"
                )
            if r_p_costs[p] < (fh_cost + min(fh_p_costs[p])):
                p_space.append(p)

        return p_space

    def gen_pq_nodes(self, ep_space, q_space):
        """
        Return a list of PQ-Nodes.

        :param str ep_space: List of P-space or EP-space nodes
        :param str q_space: List of Q-space nodes from the same graph
        :return list: List of nodes in PQ-space
        :rtype: list
        """

        """
        RFC7490:
        PQ Nodes
        The intersection of the E's Q-space with respect to S-E with, S's
        P-space with respect to S-E, defines the set of viable repair tunnel
        endpoints, known as "PQ nodes".

        The RFC doesn't mandate a method of chosen a single repair node if
        multiple exist, thus pq_nodes contians all nodes with the best cost
        to reach them (if multiple are tied).
        """
        return [node for node in ep_space if node in q_space]

    def gen_q_space(self, dst, graph, src):
        """
        Return a list of nodes in dst's Q-space.

        :param str dst: Dest node in "graph" to calculate Q-space for
        :param networkx.Graph graph: NetworkX graph object
        :param str src: Source node in "graph" relevant to S-E link
        :return q_space: List of nodes in dst's Q-space with respect to S-E
        :rtype: list
        """

        """
        RFC7490:
        Q-space
        The set of routers from which the node E can be reached, by normal
        forwarding without traversing the link S-E, is termed the Q-space of
        E with respect to the link S-E. The Q-space can be obtained by
        computing a reverse Shortest Path Tree (rSPT) rooted at E, with the
        subtree that might traverse the protected link S-E excised (i.e.,
        those nodes that would send the packet via S-E plus those nodes that
        have an ECMP set to E with one or more members of that ECMP set
        traversing the protected link S-E). The rSPT uses the cost towards
        the root rather than from it and yields the best paths towards the
        root from other nodes in the network. In the case of Figure 1, the
        Q-space of E with respect to S-E comprises nodes C and D only.
        Expressed in cost terms, the set of routers {Q} are those for which
        the shortest path cost Q<-E is strictly less than the shortest path
        cost Q<-S<-E.
        """

        q_space = []
        s_d_cost = self.spf.gen_metric_cost(dst=dst, graph=graph, src=src)

        for node in graph.nodes:

            if node == src or node == dst:
                continue

            n_d_cost = self.spf.gen_metric_cost(dst=dst, graph=graph, src=node)
            n_s_cost = self.spf.gen_metric_cost(dst=src, graph=graph, src=node)

            if self.debug > 1:
                print(
                    f"q-space {node}: {n_d_cost} < ({n_s_cost} + {s_d_cost})?"
                )
            if n_d_cost < (n_s_cost + s_d_cost):
                q_space.append(node)

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
