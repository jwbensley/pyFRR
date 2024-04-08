from __future__ import annotations

from .all_paths import AllPaths
from .node import Node
from .path import NodePath, NodePaths
from .settings import Settings
from .spf_paths import SpfPaths
from .topology import Topology


class RlfaPaths(AllPaths):
    """
    Calculate RFC5286 LFA paths between nodes in a topology
    """

    log_prefix: str = __name__

    def __init__(
        self: RlfaPaths,
        spf_paths: SpfPaths,
        topology: Topology,
        ep_space: bool = True,
        trombone: bool = False,
    ) -> None:
        self.ep_space = ep_space
        self.spf_paths: SpfPaths = spf_paths
        self.topology: Topology = topology
        self.trombone = trombone
        self.calculate_paths()

    def calculate_linkpaths(
        self: RlfaPaths, pq_nodes: list[Node], source: Node, target: Node
    ) -> NodePaths:
        """
        Return all link protecting rLFA paths from source to target.
        Do this by returning all paths between source and target, which go via
        the repair node (PQ), which is not in the pre-failure best path between
        source and target, based on weight (not hop count).

        :param list pq_nodes: List of PQ nodes from source's perspective
        :param Node source: Source node
        :param Node target: Destination node
        :return rlfas_link: List of tuples of each equal cost rLFA to target
        :rtype: list
        """

        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Calculatng rLFA link protecting paths from {source} to {target}",
        )

        """
        :param str dst: Destination node name in "graph"
        :param list pq_nodes: List of PQ nodes in "graph"
        :param str src: Source node name in "graph"
        :return rlfas_link: List of tuples of each equal cost rLFA to "dst"
        :rtype: list
        """

        """
        rlfas_link = []
        rlfa_cost = 0
        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)

        for pq in pq_nodes:
        """

        paths = NodePaths(paths=[])
        source_target_paths = self.spf_paths.get_paths_between(
            source=source, target=target
        )
        source_target_first_hops = source_target_paths.get_first_hop_nodes()
        for pq_node in pq_nodes:
            """
            RFC7490:
            Exclude the first-hop node(s) (E) along the best-path(s) toward dst.
            They may technically fall into pq_space but if the first-hop link
            (S-E) is down, they won't be the closet pq_nodes anymore.
            """
            """
            if pq in [path[1] for path in s_d_paths]:
                continue
            """
            if pq_node in source_target_first_hops:
                continue

            ######if pq_node == source:
            ###########    continue

            """
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
            # Create a tuple of the path(s) from src to pq and the path(s)
            # from pq to dst
            """
                rlfas_link = [([path for path in s_pq_paths], pq_dst_paths)]
                rlfa_cost = s_pq_cost
                if self.debug > 0:
                    print(
                        f"New link rLFA cost: {rlfa_cost}, path(s): {rlfas_link}"
                    )
            """
            source_pq_paths = self.spf_paths.get_paths_between(
                source=source, target=pq_node
            )
            # if (
            #    source_pq_paths.get_lowest_path_weight() < rlfa_cost
            #    or rlfa_cost == 0
            # ):
            pq_target_paths = self.spf_paths.get_paths_between(
                source=pq_node, target=target
            )
            # If trumboning is disabled, check if this is a tumbone path:
            if not self.trombone:
                skip = False
                source_pq_path: NodePath
                for source_pq_path in source_pq_paths:
                    source_pq_hop: Node
                    for source_pq_hop in source_pq_path[:-1]:
                        pq_target_path: NodePath
                        for pq_target_path in pq_target_paths:
                            if source_pq_hop in pq_target_path[1:]:
                                self._log(
                                    level=Settings.LOG_DEBUG,
                                    msg=f"Skipping trombone link rLFA "
                                    f"{(source_pq_path,pq_target_path)}",
                                )
                                skip = True
                                break
                        if skip:
                            break
                    if skip:
                        break
                if skip:
                    continue

            for source_pq_path in source_pq_paths:
                for pq_target_path in pq_target_paths:
                    backup_path = NodePath(
                        path=(
                            source_pq_path.get_nodes()[:-1]
                            + pq_target_path.get_nodes()
                        )
                    )
                    backup_path.set_link_protecting(True)
                    paths.append(backup_path)

        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Link rLFA paths from {source} to {target}: {paths}",
        )
        return paths

    def calculate_nodepaths(  # type: ignore[override]
        self: RlfaPaths,
        source: Node,
        target: Node,
        pq_nodes: list[Node],
    ) -> NodePaths:
        """
        Return NodePaths of rLFA paths between the source and target
        nodes based on weight (not hop count), which provide link or node
        protection.

        :param list pq_nodes: List of PQ nodes from source's perspective
        :param Node source: Source node in the topology
        :param Node target: Target node in the topology
        :rtype: NodePaths
        """

        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Calculatng rLFA node paths from {source} to {target}",
        )

        """
        def gen_metric_paths_node(self, dst, graph, rlfas_link, src):
        Return all node protecting rLFAs.
        Do this by filtering the list of link rLFAs "rlfas_link" for those
        with pre-convergence best path(s) from all repair tunnel end-points
        {p}, which don't pass through any of the first-hops of any of the
        pre-convergence best-paths from src to dst.

        :param str dst: Destination node name in "graph"
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

        """
        rlfas_node = []
        s_d_paths = self.spf.gen_metric_paths(dst=dst, graph=graph, src=src)
        s_d_fhs = [path[1] for path in s_d_paths]
        for s_pq_paths, pq_dst_paths in rlfas_link:
            overlap = [
                fh
                for fh in s_d_fhs
                for p_d_path in pq_dst_paths
                if fh in p_d_path
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

                rlfas_node.append((s_pq_paths, pq_dst_paths))

        return rlfas_node
        """
        paths = NodePaths(paths=[])
        source_target_paths = self.spf_paths.get_paths_between(
            source=source, target=target
        )
        source_target_first_hops = source_target_paths.get_first_hop_nodes()

        for pq_node in pq_nodes:
            if pq_node in source_target_first_hops:
                continue

            source_pq_paths = self.spf_paths.get_paths_between(
                source=source, target=pq_node
            )
            pq_target_paths = self.spf_paths.get_paths_between(
                source=pq_node, target=target
            )

            overlap = [
                source_target_fh
                for source_target_fh in source_target_first_hops
                for pq_target_path in pq_target_paths
                if source_target_fh in pq_target_path
            ]
            if overlap:
                self._log(
                    level=Settings.LOG_DEBUG,
                    msg=f"rLFA path {(source_pq_paths, pq_target_paths)} is not "
                    f"node  protecting against {overlap} from {source} to "
                    f"{target}",
                )
            else:
                # If trumboning is disabled, check if this is a tumbone path:
                if not self.trombone:
                    skip = False
                    source_pq_path: NodePath
                    for source_pq_path in source_pq_paths:
                        source_pq_hop: Node
                        for source_pq_hop in source_pq_path[:-1]:
                            pq_target_path: NodePath
                            for pq_target_path in pq_target_paths:
                                if source_pq_hop in pq_target_path[1:]:
                                    self._log(
                                        level=Settings.LOG_DEBUG,
                                        msg=f"Skipping trombone node rLFA "
                                        f"{(source_pq_path, pq_target_path)}",
                                    )
                                    skip = True
                                    break
                            if skip:
                                break
                        if skip:
                            break
                    if skip:
                        continue

                for source_pq_path in source_pq_paths:
                    for pq_target_path in pq_target_paths:
                        backup_path = source_pq_path + pq_target_path
                        backup_path.set_link_protecting(True)
                        paths.append(backup_path)

        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Link rLFA paths from {source} to {target}: {paths}",
        )
        return paths

    def calculate_paths(self: RlfaPaths) -> None:
        """
        Filter rlfa_paths for the NodePaths between all nodes in the topology,
        which are rLFA paths.

        :rtype: None
        """
        self._log(level=Settings.LOG_INFO, msg="Calculating all paths...")

        self.paths = {}
        for source in self.topology.get_nodes_list():
            self.paths[source] = {}
            for target in self.topology.get_nodes_list():
                if source == target:
                    continue
                self.paths[source][target] = self.calculate_rlfa_paths(
                    source=source,
                    target=target,
                )

        self._log(level=Settings.LOG_INFO, msg=f"Calculated {len(self)} paths")

    def calculate_rlfa_paths(
        self: RlfaPaths, source: Node, target: Node
    ) -> NodePaths:
        """
        Return a NodePaths obj of link and node protecting paths,
        from source to target.

        :param Node source: Source node in the topology
        :param Node target: Target node in the topology
        :rtype: NodePaths
        """

        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Calculating rLFA paths from {source} to {target}",
        )

        """
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
        """

        q_space = self.gen_q_space(source=source, target=target)

        if self.ep_space:
            ep_space = self.gen_ep_space(source=source, target=target)
            pq_nodes = self.gen_pq_nodes(ep_space=ep_space, q_space=q_space)
        else:
            p_space = self.gen_p_space(
                root=source, source=source, target=target
            )
            pq_nodes = self.gen_pq_nodes(ep_space=p_space, q_space=q_space)

        rlfa_paths = self.calculate_linkpaths(
            pq_nodes=pq_nodes, source=source, target=target
        )
        for path in self.calculate_nodepaths(
            source=source,
            target=target,
            pq_nodes=pq_nodes,
        ):
            rlfa_paths.append(path)

        return rlfa_paths

    def gen_ep_space(
        self: RlfaPaths, source: Node, target: Node
    ) -> list[Node]:
        """
        Return a list of nodes in source's Extended P-space.

        :param Node source: Source node to calculate EP-space (via S-E link)
        :param Node target: Target node to calculate EP-space (via S-E link)
        :return ep_space: Nodes in sources's EP-space with respect to S-E
        :rtype: list
        """
        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Calculating EP-space from {source} to {target}",
        )

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
        """

        ep_space: set[Node] = set()
        for nei in source.get_neighbours():
            if nei == target:
                continue

            nei_p_space = self.gen_p_space(
                root=nei, source=source, target=target
            )
            for pnode in nei_p_space:
                if pnode == source:
                    continue

                nei_pnode_cost = self.spf_paths.get_path_cost_between(
                    source=nei, target=pnode
                )
                nei_source_cost = self.spf_paths.get_path_cost_between(
                    source=nei, target=source
                )
                source_target_cost = self.spf_paths.get_path_cost_between(
                    source=source, target=target
                )
                target_pnode_cost = self.spf_paths.get_path_cost_between(
                    source=target, target=pnode
                )
                if nei_pnode_cost < (
                    nei_source_cost + source_target_cost + target_pnode_cost
                ):
                    self._log(
                        level=Settings.LOG_DEBUG,
                        msg=f"EP-space for {source}: adding "
                        f"{nei} {nei_pnode_cost} < ({nei_source_cost} + "
                        f"{source_target_cost} + {target_pnode_cost})",
                    )
                    ep_space.add(pnode)

        self._log(
            level=Settings.LOG_DEBUG, msg=f"EP-space for {source}: {ep_space}"
        )
        return list(ep_space)

    def gen_p_space(
        self: RlfaPaths,
        root: Node,
        source: Node,
        target: Node,
    ) -> list[Node]:
        """
        Return a list of nodes in root's P-space relevant to the first-hop
        link(s) from source to target.
        When calculating P-space for node X, root == X, src == X.
        When calculating X's EP-space, root == neighbour of X, src == X.

        :param Node root: Root node to calcuate P-space from
        :param Node source: Source node which must avoid S-E link to target
        :param Node target: Node to calculate P-space toward, avoiding S-E
        :return p_space: List of nodes in root's P-space with respect to S-E
        :rtype: list
        """

        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Calculating P-space for {root} no via {source} to {target}",
        )

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

        p_space: list[Node] = []

        """
        Find the cost of the lowest cost first-hop from all the best paths
        towards the target node, and build a list of all first-hops toward target.
        When ECMP is used in the pre-convergence state, the rLFA remote tunnel
        endpoint (p) must not be a first-hop along another of the ECMP paths.
        """
        print(f"Source to target:")
        print(self.spf_paths.get_paths_between(source=source, target=target))
        print(f"Root to target:")
        print(self.spf_paths.get_paths_between(source=root, target=target))

        root_target_paths = self.spf_paths.get_paths_between(
            source=root, target=target
        )
        if not root_target_paths:
            self._log(
                level=Settings.LOG_DEBUG, msg=f"{root}'s P-space is empty"
            )
            return p_space

        root_target_fh_nodes = root_target_paths.get_first_hop_nodes()
        root_pnode_costs = {}
        fh_pnode_costs: dict[Node, list] = {}
        for pnode in self.topology.get_nodes_list():
            if pnode in [root, source, target]:
                continue

            """
            RFC7490:
            ...excising the subtree reached via the link S-E (including those
            routers that are members of an ECMP that includes link S-E).
            """
            if not (
                pnode_target_paths := self.spf_paths.get_paths_between(
                    source=pnode, target=target
                )
            ):
                self._log(
                    level=Settings.LOG_DEBUG,
                    msg=f"No path from {pnode} to {target}",
                )
                continue

            """
            Check if source is a hop in any P-node-to-target paths
            """
            self._log(
                level=Settings.LOG_DEBUG,
                msg=f"Checking if {pnode} to {target} is via {source}",
            )
            if source in [
                source for path in pnode_target_paths if source in path
            ]:
                self._log(
                    level=Settings.LOG_DEBUG,
                    msg=f"Skipping node {pnode} with {source} "
                    f"in it's best path(s) toward {target}:\n"
                    f"{pnode_target_paths}",
                )
                continue

            self._log(
                level=Settings.LOG_DEBUG, msg=f"{pnode} is a candidate pnode"
            )
            root_pnode_costs[pnode] = self.spf_paths.get_path_cost_between(
                source=root, target=pnode
            )

            fh_pnode_costs[pnode] = []
            for root_target_fh in root_target_fh_nodes:
                if root_target_fh == pnode:
                    continue  # ????????????????????????????????????????????????????????????????????????
                fh_pnode_costs[pnode].append(
                    self.spf_paths.get_path_cost_between(
                        source=root_target_fh, target=pnode
                    )
                )

        root_target_fh_cost = root_target_paths.get_lowest_path_weight()
        for pnode in root_pnode_costs:
            """
            Because this function is used calculate both the P-Space for src
            and the EP-space of src's neighbours, in the later case a neighbour
            of src may choose a P node which is via the S-E link
            """
            source_pnode_paths = self.spf_paths.get_paths_between(
                source=source, target=pnode
            )
            if target in [
                target for path in source_pnode_paths if target in path
            ]:
                self._log(
                    level=Settings.LOG_DEBUG,
                    msg=f"Skipping node {pnode} with target "
                    f"{target} in the best path(s) from {source} to {pnode}: "
                    f"{source_pnode_paths}",
                )
                continue

            """
            RFC7490:
            Expressed in cost terms, the set of routers {P} are those for which
            the shortest path cost S->P is strictly less than the shortest path
            cost S->E->P.
            """
            if root_pnode_costs[pnode] < (
                root_target_fh_cost + min(fh_pnode_costs[pnode])
            ):
                self._log(
                    level=Settings.LOG_DEBUG,
                    msg=f"P-space for {root}: adding {pnode}: "
                    f"{root_pnode_costs[pnode]}<({root_target_fh_cost} + "
                    f"{min(fh_pnode_costs[pnode])})",
                )
                p_space.append(pnode)

        self._log(
            level=Settings.LOG_DEBUG, msg=f"P-space for {root}: {p_space}"
        )
        return p_space

    def gen_pq_nodes(
        self: RlfaPaths, ep_space: list[Node], q_space: list[Node]
    ) -> list[Node]:
        """
        Return a list of PQ-Nodes.

        :param list ep_space: List of P-space or EP-space nodes
        :param list q_space: List of Q-space nodes from the same graph
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
        pq_nodes = [node for node in ep_space if node in q_space]
        self._log(level=Settings.LOG_DEBUG, msg=f"PQ-nodes: {pq_nodes}")
        return pq_nodes

    def gen_q_space(self: RlfaPaths, source: Node, target: Node) -> list:
        """
        Return a list of nodes in targets's Q-space.

        :param Node source: Source node relevant to S-E link
        :param Node target: Target node to calculate Q-space for
        :return q_space: List of nodes in targets's Q-space with respect to S-E
        :rtype: list
        """
        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Calculating Q-space from {source} to {target}",
        )

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
        q_space: list[Node] = []
        source_target_cost = self.spf_paths.get_path_cost_between(
            source=source, target=target
        )

        for node in self.topology.get_nodes_list():
            if node == source or node == target:
                continue

            node_source_cost = self.spf_paths.get_path_cost_between(
                source=node, target=source
            )
            node_target_cost = self.spf_paths.get_path_cost_between(
                source=node, target=target
            )

            if node_target_cost < (node_source_cost + source_target_cost):
                self._log(
                    level=Settings.LOG_DEBUG,
                    msg=f"Q-space for {source}: adding {node} "
                    f"{node_target_cost} < ({node_source_cost} + "
                    f"{source_target_cost})",
                )
                q_space.append(node)

        self._log(
            level=Settings.LOG_DEBUG, msg=f"Q-space for {source}: {q_space}"
        )
        return q_space
