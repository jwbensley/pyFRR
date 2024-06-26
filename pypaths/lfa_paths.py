from __future__ import annotations

from .all_paths import AllPaths
from .node import Node
from .path import NodePath, NodePaths
from .settings import Settings
from .spf_paths import SpfPaths
from .topology import Topology


class LfaPaths(AllPaths):
    """
    Calculate RFC5286 LFA paths between nodes in a topology
    """

    log_prefix: str = __name__

    def __init__(
        self: LfaPaths, spf_paths: SpfPaths, topology: Topology
    ) -> None:
        self.spf_paths: SpfPaths = spf_paths
        self.topology: Topology = topology
        self.calculate_paths()

    def calculate_nodepaths(  # type: ignore[override]
        self: LfaPaths,
        source: Node,
        target: Node,
    ) -> NodePaths:
        """
        Return a NodePaths list of LFA paths between the source and target nodes
        based on weight (not hop count), which provide link or node protection.

        :param Node source: Source node in the topology
        :param Node target: Target node in the topology
        :rtype: NodePaths
        """

        lfa_paths: NodePaths = NodePaths(paths=[])
        self._log(
            level=Settings.LOG_DEBUG,
            msg=f"Calculating paths from {source} to {target}",
        )

        if not (
            source_target_paths := self.spf_paths.get_paths_between(
                source, target
            )
        ):
            return lfa_paths

        # Loop over each neighbour to check if each one is an LFA candidate
        for nei in source.neighbours:
            # If target is directly connceted
            if nei == target:
                continue

            # This nei is the next-hop for the current best path(s)
            if nei in source_target_paths.get_first_hop_nodes():
                self._log(
                    level=Settings.LOG_DEBUG,
                    msg=f"Rejected paths via {nei}, it is a "
                    f"next-hop in the current best path(s):\n"
                    f"{source_target_paths}",
                )
                continue

            """
            ECMP may be used meaning the source has multiple equal cost best
            paths to target. And/or, nei may have multiple equal cost best
            paths to target.

            Regardless of the number of paths, they are the same cost, so only
            check the cost of the first best path of source against the first
            best path of nei.
            """
            any_best_path = source_target_paths[0]
            nh = any_best_path[1]

            if (
                not (
                    nei_target_cost := self.spf_paths.get_paths_between(
                        nei, target
                    ).get_lowest_path_weight()
                )
                or not (
                    nei_source_cost := self.spf_paths.get_paths_between(
                        nei, source
                    ).get_lowest_path_weight()
                )
                or not (
                    source_target_cost := self.spf_paths.get_paths_between(
                        source, target
                    ).get_lowest_path_weight()
                )
                or not (
                    nei_nh_cost := self.spf_paths.get_paths_between(
                        nei, nh
                    ).get_lowest_path_weight()
                )
                or not (
                    nh_target_cost := self.spf_paths.get_paths_between(
                        nh, target
                    ).get_lowest_path_weight()
                )
            ):
                # There isn't connectivity between the nodes; source, target, nh, nei
                continue

            self._log(
                level=Settings.LOG_DEV,
                msg=f"{nei} -> {target}: {nei_target_cost}\n"
                f"{nei} -> {source}: {nei_source_cost}\n"
                f"{source} -> {target}: {source_target_cost}\n"
                f"{nei} -> {nh}: {nei_nh_cost}\n"
                f"{nh} -> {target}: {nh_target_cost}",
            )

            link_prot: bool = False
            down_prot: bool = False
            node_prot: bool = False

            """
            RFC5286:
            Inequality 1: Loop-Free Criterion
            A neighbor N of source S can provide a loop-free alternate (lfa)
            toward destination D, that is link protecting, iff:
            Distance_opt(N, D) < Distance_opt(N, S) + Distance_opt(S, D)

            In this scenario, N's cost to D is lower than (N's cost to S) + (S's
            cost to D), so N must have an alternative path to D not via S, but
            S and N might be sharing the same next-hop router, and N simply
            has another link to that shared next-hop router, so it is link
            protecting only, for S's link to it's next-hop.
            """
            if nei_target_cost < (nei_source_cost + source_target_cost):
                # nei protects src against link failure to next-hop toward dst
                link_prot = True
                self._log(
                    level=Settings.LOG_DEV,
                    msg=f"{nei} to {target} < ({nei} to {source}"
                    f") + ({source} to {target}), {nei_target_cost} < "
                    f"{nei_source_cost + source_target_cost}",
                )

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
            if nei_target_cost < (source_target_cost):
                # nei protects src against failure of link or node toward dst
                down_prot = True
                self._log(
                    level=Settings.LOG_DEV,
                    msg=f"{nei} to {target} < {source} to "
                    f"{target}: {nei_target_cost} < {nei_source_cost}",
                )

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
            if nei_target_cost < (nei_nh_cost + nh_target_cost):
                # nei protects src against next-hop node failure toward dst
                node_prot = True
                self._log(
                    level=Settings.LOG_DEV,
                    msg=f"{nei} to {target} < ({nei} to {nh} + "
                    f"{nh} to {source}), {nei_target_cost} < "
                    f"{nei_nh_cost + nh_target_cost}",
                )

            # nei might have multiple equal-cost best paths to target
            nei_target_paths = self.spf_paths.get_paths_between(nei, target)

            """
            Mark each path from source, via nei, to target with it's
            protection type and append to the list of LFA paths:
            """
            nei_target_path: NodePath
            for nei_target_path in nei_target_paths:
                # Prepend source to nei_target_path to create full LFA path
                lfa_path = NodePath(path=[source] + list(nei_target_path))
                self._log(
                    level=Settings.LOG_DEBUG, msg=f"Candidate path: {lfa_path}"
                )
                if link_prot:
                    lfa_path.set_link_protecting(True)
                    lfa_paths.append(lfa_path)
                    self._log(
                        level=Settings.LOG_DEBUG,
                        msg=f"New link protecting path from "
                        f"{source} to {target} via {nei}, protects against "
                        f"link {source}-{nh}: {lfa_path}",
                    )

                if down_prot:
                    lfa_path.set_down_protecting(True)
                    lfa_paths.append(lfa_path)
                    self._log(
                        level=Settings.LOG_DEBUG,
                        msg=f"New downstream protecting path "
                        f"from {source} to {target} via {nei}: {lfa_path}",
                    )

                if node_prot:
                    """
                    In order to protect pre-failure ECMP best-paths, check that
                    this node protecting path doesn't overlap with any of the
                    ECMP next-hop nodes
                    """
                    source_target_first_hops = (
                        source_target_paths.get_first_hop_nodes()
                    )
                    overlap = [
                        fh
                        for fh in source_target_first_hops
                        for nei_target_path in nei_target_paths
                        if fh in nei_target_path
                    ]
                    if overlap:
                        self._log(
                            level=Settings.LOG_DEBUG,
                            msg=f"Path {lfa_path} is not node "
                            f"protecting against {overlap} from {source} to "
                            f"{target}",
                        )
                        continue

                    lfa_path.set_node_protecting(True)
                    lfa_paths.append(lfa_path)
                    self._log(
                        level=Settings.LOG_DEBUG,
                        msg=f"New node protecting path from "
                        f"{source} to {target} via {nei}, protects against "
                        f"node {nh}: {lfa_path}",
                    )

        return lfa_paths

    def calculate_paths(self: LfaPaths) -> None:
        """
        Filter spf_paths for the NodePaths between all nodes in the topology,
        which are LFA paths.

        :rtype: None
        """
        self._log(
            level=Settings.LOG_INFO,
            msg=f"Calculating all paths...",
        )

        self.paths = {}
        for source in self.topology.get_nodes_list():
            self.paths[source] = {}
            for target in self.topology.get_nodes_list():
                if source == target:
                    continue
                self.paths[source][target] = self.calculate_nodepaths(
                    source=source,
                    target=target,
                )

        self._log(level=Settings.LOG_INFO, msg=f"Calculated {len(self)} paths")
