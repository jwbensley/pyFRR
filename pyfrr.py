from datetime import datetime
import json
import networkx as nx
import os
import pydot

from base import Base
from diagram import Diagram
from lfa import lfa
from rlfa import rlfa
from spf import spf
from tilfa import tilfa


class pyfrr:
    """This is the parent class for the pyFRR module"""

    def __init__(
        self,
        debug=0,
        ep_space=True,
        filename=None,
        filetype=None,
        graph=None,
        links=None,
        nodes=None,
        trombone=False,
    ):
        """
        Exactly one type of input data must be passed to this class:
        - Two lists of dicts (links and nodes)
        - Two strings (filename and filetype)
        - A NetworkX graph

        :param int debug: Debugging level
        :param bool ep_space: rlfa, toggle calculating ep_space or p_space only
        :param str filename: Topology filename to load if loading from file
        :param str filetype: Topology filename type if loading from file
        :param networkx.Graph graph: NetworkX graph object if using existing
        :param list links: List of dicts, each dict is a link between two nodes
        :param list nodes: List of dicts, each dict is a node in the network
        :param bool trombone: rlfa, allow/disallow rlfas that trombone p node
        :return None: __init__ shouldn't to return anything
        :rtype: None
        """

        self.base = Base(debug=debug)
        self.debug = debug
        self.diagram = Diagram(debug=debug)
        self.ep_space = ep_space
        self.filename = filename
        self.filetype = filetype
        self.graph = None
        self.lfa = lfa(debug=debug)
        self.links = links
        self.nodes = nodes
        self.outdir = None
        self.rlfa = rlfa(debug=debug, ep_space=ep_space, trombone=trombone)
        self.spf = spf(debug=debug)
        self.tilfa = tilfa(debug=debug)
        self.topo = {}
        self.trombone = trombone

        if type(graph) == nx.classes.graph.Graph:
            self.graph = graph.copy()

        elif self.filename and self.filetype:
            if self.filetype.lower() == "json":
                self.load_json(self.filename)

            elif self.filetype.lower() == "dot":
                self.load_dot(self.filename)

            else:
                raise Exception(f"Unrecognised file type {self.filetype}")

            if self.debug > 0:
                print(f"Graph created from file {filename}")

        elif type(self.links) == list and type(self.nodes) == list:
            self.parse_json(self.links, self.nodes)

        else:
            raise Exception(
                "Insufficient network topology data provided. You must pass"
                " two dicts (links=[] and nodes=[]) for a network graph to "
                "be built from, or two strings (filename='', filetype='') to "
                "load and parse a file, or an existing NetworkX graph (graph=)"
            )

        # Generate the dict keys for all path types between all src/dst pairs:
        self.init_topo()

        if self.debug > 0:
            print(
                f"Created topology with {len(self.graph.nodes)} nodes and "
                f"{len(self.graph.edges)} links"
            )

    def check_topo(self):
        """
        If the graph has changed (nodes were added or removed) since this
        function was last run, whipe out all existing data, it is no longer
        valid.

        :return None:
        :rtype: None
        """
        for src in self.graph.nodes:
            if src not in self.topo:
                self.init_topo()

        for src in self.topo:
            if src not in self.graph.nodes:
                self.init_topo()

    def diagram_init(self):
        """
        Create the diagram base output directory.

        :return None: On success update the self stored outdir string or raise
        an exception
        :rtype: None
        """

        if self.filename:
            try:
                topo_name = os.path.splitext(os.path.basename(self.filename))[0]
            except Exception:
                print(
                    "Couldn't create output directory name from input filename"
                )
                raise

            outdir = os.path.join(
                os.path.curdir,
                "diagrams",
                topo_name,
                datetime.now().strftime("%Y-%m-%d--%H-%M-%S-%f"),
            )

        else:
            outdir = os.path.join(
                os.path.curdir,
                "diagrams",
                datetime.now().strftime("%Y-%m-%d--%H-%M-%S-%f"),
            )

        self.diagram.gen_root_dir(outdir)
        #raise Exception("Diagram output directory tree creation failed")

        self.outdir = outdir

    def draw(self, outdir=None, types=[]):
        """
        Render the calculated paths as diagrams.

        :param str outdir: Output directory for rendered diagram images
        :param list types: List of path types to render as diagrams
        :return str d: Return the output directory string on success
        :rtype: bool
        """

        if outdir:
            d = outdir
        else:
            if not self.outdir:
                self.diagram_init()
            d = self.outdir

        for t in types:
            if t == "base":
                self.base.draw(self.graph, d, self.topo)

            if t == "spf":
                self.spf.draw(self.graph, d, self.topo)

            if t == "lfa":
                """
                Before LFAs can be rendered, the SPF paths must have been
                calculated if they weren't already, or if the topology was
                modified since the last run
                """
                self.gen_all_metric_spfs()
                self.lfa.draw(self.graph, d, self.topo)

            if t == "rlfa":
                """
                Before rLFAs can be rendered, the SPF paths must have been
                calculated if they weren't already, or if the topology was
                modified since the last run
                """
                self.gen_all_metric_spfs()
                self.rlfa.draw(self.graph, d, self.topo)

            if t == "tilfa":
                """
                Before TI-LFAs can be rendered, the SPF paths must have been
                calculated if they weren't already, or if the topology was
                modified since the last run
                """
                self.gen_all_metric_spfs()
                self.tilfa.draw(self.graph, d, self.topo)

        return d

    def draw_base(self, outdir=None):
        """
        Render the base topology diagram (the loaded topology with
        nothing highlighted).

        :param str outdir: Output directory for rendered diagram images
        :return str d: Return the output directory string on success
        :rtype: bool
        """

        return self.draw(outdir, ["base"])

    def draw_lfas(self, outdir=None):
        """
        Render all the calculated lfa paths as diagram files.

        :param str outdir: Output directory for rendered diagram images
        :return str d: Return the output directory string on success
        :rtype: bool
        """

        return self.draw(outdir, ["lfa"])

    def draw_rlfas(self, outdir=None):
        """
        Render all the calculated rlfa paths as diagram files.

        :param str outdir: Output directory for rendered diagram images
        :return str d: Return the output directory string on success
        :rtype: bool
        """

        return self.draw(outdir, ["rlfa"])

    def draw_tilfas(self, outdir=None):
        """
        Render all the calculated TI-lfa paths as diagram files.

        :param str outdir: Output directory for rendered diagram images
        :return str d: Return the output directory string on success
        :rtype: bool
        """

        return self.draw(outdir, ["tilfa"])

    def draw_spf(self, outdir=None):
        """
        Render all the calculated shortest paths as diagram files.

        :param str outdir: Output directory for rendered diagram images
        :return str d: Return the output directory string on success
        :rtype: bool
        """
        
        return self.draw(outdir, ["spf"])

    def gen_all_metric_lfas(self):
        """
        Calculate all equal cost lfa paths (based on link metric,
        not hop count) between all nodes in self.graph.

        :param networkx.Graph graph: NetworkX graph object
        :return None: Updates the self stored topology dictionary
        :rtype: None
        """

        self.check_topo()

        for src in self.graph.nodes:
            for dst in self.graph.nodes:
                if src == dst:
                    continue

                """
                Whipe out any existing path data incase links/edges were added
                to or removed from graph since this function was last run:
                """
                self.lfa.init_topo(self.graph, self.topo)

                lfas = self.lfa.gen_metric_paths(dst, self.graph, src)
                self.topo[src][dst].update(lfas)

    def gen_all_metric_rlfas(self):
        """
        Calculate all equal cost rlfa paths (based on link metric,
        not hop count) between all nodes in self.graph.

        :param networkx.Graph graph: NetworkX graph object
        :return None: Updates the self stored topology dictionary
        :rtype: None
        """

        self.check_topo()

        for src in self.graph.nodes:
            for dst in self.graph.nodes:
                if dst == src:
                    continue

                """
                Whipe out any existing path data incase links/edges were added
                or removed from graph, since this function was last run:
                """
                self.rlfa.init_topo(self.graph, self.topo)

                rlfas = self.rlfa.gen_metric_paths(dst, self.graph, src)
                self.topo[src][dst].update(rlfas)

    def gen_all_metric_spfs(self):
        """
        Calculate all equal cost shotest paths between every node in
        self.graph.

        :param networkx.Graph graph: NetworkX graph object
        :return None: Updates the self stored topology dictionary
        :rtype: None
        """

        self.check_topo()

        for src in self.graph.nodes:
            for dst in self.graph.nodes:
                if src == dst:
                    continue

                """
                Whipe out any existing path data incase links/edges were added
                to or removed from graph since this function was last run:
                """
                self.spf.init_topo(self.graph, self.topo)

                self.topo[src][dst]["cost"] = self.spf.gen_metric_paths(
                    dst, self.graph, src
                )

    def gen_all_metric_tilfas(self):
        """
        Calculate all equal cost TI-lfa paths (based on link metric,
        not hop count) between all nodes in self.graph.

        :param networkx.Graph graph: NetworkX graph object
        :return None: Updates the self stored topology dictionary
        :rtype: None
        """

        self.check_topo()

        #self.tilfa.init_topo(self.graph, self.topo)
        #tilfas = self.tilfa.gen_metric_paths("P1", self.graph, "PE1")
        #self.topo["PE1"]["P1"].update(tilfas)
        #return ##########################################################

        for src in self.graph.nodes:
            for dst in self.graph.nodes:
                if dst == src:
                    continue

                """
                Whipe out any existing path data incase links/edges were added
                to or removed from graph since this function was last run:
                """
                self.tilfa.init_topo(self.graph, self.topo)

                tilfas = self.tilfa.gen_metric_paths(dst, self.graph, src)
                self.topo[src][dst].update(tilfas)
            return #############################################################

    def get_paths(self, dst=None, src=None):
        """
        Return the path dict's for all nodes in the graph if no src or dst.
        If only src is given, return all paths from src to all other nodes.
        If only dst is given, return all paths to dst from all other nodes.
        If src AND dst are given, return all paths from src and dst.

        :param str src: Name of source node in network topology
        :param str dst: Name of destination node in network topology
        :return dict: Dict of requested paths
        :rtype: dict
        """

        if src == dst:
            return {}

        if src:
            if src not in self.topo:
                raise Exception("Source node not in topology data")
            if not dst:
                return self.topo[src]
            if dst:
                if dst not in self.topo[src]:
                    raise Exception("Destination node not in topology data")
                return self.topo[src][dst]

        if dst:
            if dst not in [d for s in self.topo for d in self.topo[s]]:
                raise Exception("Destination node not in topology data")
            paths = {}
            for src in self.topo:
                if src == dst:
                    continue
                paths[src] = self.topo[src][dst]
            return paths

        return self.topo

    def get_paths_via(self, via):
        """
        Return the path dict's for all nodes in the graph who have paths via
        node "via". It can not be the source or destination node.

        :param str via: Node in network topology the paths must pass through
        :return dict: Dict of requested paths
        :rtype: dict
        """

        if via not in self.graph.nodes:
            raise Exception("Via node not in topology data")

        paths = {}

        for src, dst in [
            (s, d) for d in self.graph.nodes for s in self.graph.nodes
        ]:

            if src == dst:
                continue

            if src == via or dst == via:
                continue

            for path in self.topo[src][dst]["cost"]:
                if via in path[1:-1]:

                    if src not in paths:
                        paths[src] = {}
                    if dst not in paths[src]:
                        paths[src][dst] = {}
                    if "cost" not in paths[src][dst]:
                        paths[src][dst]["cost"] = []

                    paths[src][dst]["cost"].append(path)

            for path in self.topo[src][dst]["lfas_dstream"]:
                if via in path[1:-1]:

                    if src not in paths:
                        paths[src] = {}
                    if dst not in paths[src]:
                        paths[src][dst] = {}
                    if "lfas_dstream" not in paths[src][dst]:
                        paths[src][dst]["lfas_dstream"] = []
                    paths[src][dst]["lfas_dstream"].append(path)

            for path in self.topo[src][dst]["lfas_link"]:
                if via in path[1:-1]:

                    if src not in paths:
                        paths[src] = {}
                    if dst not in paths[src]:
                        paths[src][dst] = {}
                    if "lfas_link" not in paths[src][dst]:
                        paths[src][dst]["lfas_link"] = []
                    paths[src][dst]["lfas_link"].append(path)

            for path in self.topo[src][dst]["lfas_node"]:
                if via in path[1:-1]:

                    if src not in paths:
                        paths[src] = {}
                    if dst not in paths[src]:
                        paths[src][dst] = {}
                    if "lfas_node" not in paths[src][dst]:
                        paths[src][dst]["lfas_node"] = []
                    paths[src][dst]["lfas_node"].append(path)

            for path in self.topo[src][dst]["rlfas_link"]:
                for s_p_path in path[0]:
                    for p_d_path in path[1]:
                        if via in s_p_path[1:-1] or via in p_d_path[1:-1]:
                            if src not in paths:
                                paths[src] = {}
                            if dst not in paths[src]:
                                paths[src][dst] = {}
                            if "rlfas_link" not in paths[src][dst]:
                                paths[src][dst]["rlfas_link"] = []
                            #paths[src][dst]["rlfas_link"].append(path)
                            paths[src][dst]["rlfas_link"].append(s_p_path + p_d_path[1:])

            for path in self.topo[src][dst]["rlfas_node"]:
                for s_p_path in path[0]:
                    for p_d_path in path[1]:
                        if via in s_p_path[1:-1] or via in p_d_path[1:-1]:

                            if src not in paths:
                                paths[src] = {}
                            if dst not in paths[src]:
                                paths[src][dst] = {}
                            if "rlfas_node" not in paths[src][dst]:
                                paths[src][dst]["rlfas_node"] = []
                            #paths[src][dst]["rlfas_node"].append(path)
                            paths[src][dst]["rlfas_node"].append(s_p_path + p_d_path[1:])

        return paths

    def graph_to_json(self):
        """
        Return the NetworkX graph encoded as a JSON string.

        :return str: JSON encoding of NetworkX graph
        :rtype: str
        """

        try:
            j = json_graph.node_link_data(self.graph)
        except Exception:
            raise("Failed to convert the NetwrokX graph to JSON")

        return j

    def init_topo(self):
        """
        Generate the dict keys for all path types between all src/dst pairs:

        :return None:
        :rtype: None
        """

        self.topo = {}
        self.base.init_topo(self.graph, self.topo)
        self.spf.init_topo(self.graph, self.topo)
        self.lfa.init_topo(self.graph, self.topo)
        self.rlfa.init_topo(self.graph, self.topo)
        self.tilfa.init_topo(self.graph, self.topo)

    def load_dot(self, filename):
        """
        Build the NetworkX graph from the contents of topology DOT file.

        :param str filename: string of the DOT file to load
        :return bool True: True if NetworkX graph object created from dot file
        :rtype: bool
        """

        try:
            """
            If the DOT file is not a strict graph, read_dot() will generate a
            NetworkX multi-graph. Graph() always generates an undirected graph.
            Pass the DOT graph through Graph() to ensure it's undirected.
            """
            self.graph = nx.Graph(nx.drawing.nx_pydot.read_dot(filename))

            # When loading a dot file, the weigth int is parsed as a str:
            for edge in self.graph.edges:
                if "weight" in self.graph.edges[edge]:
                    if type(self.graph.edges[edge]["weight"]) == str:
                        i = int(self.graph.edges[edge]["weight"])
                        self.graph.edges[edge].pop("weight")
                        self.graph.edges[edge]["weight"] = i

        except Exception:
            print(f"Couldn't open topology file {filename}")
            raise

    def load_json(self, filename):
        """
        Build the NetworkX graph from the contents of topology JSON file.

        :param str filename: string of the JSON file to load
        :return bool True: True if NetworkX graph object created from dot file
        :rtype: bool
        """

        try:
            topo_file = open(filename, "r")
        except Exception:
            print(f"Couldn't open topology file {filename}")
            raise

        try:
            topo_json = json.load(topo_file)
        except Exception:
            print(f"Couldn't parse topology JSON from file {filename}")
            raise

        topo_file.close()

        # Add in the field required by NetworkX
        if "directed" not in topo_json:
            topo_json["directed"] = False
        if "multigraph" not in topo_json:
            topo_json["multigraph"] = False

        # Create the node/edge graph from the JSON topology data:
        try:
            self.graph = nx.readwrite.json_graph.node_link_graph(topo_json)
        except Exception:
            print("Couldn't convert topology JSON data to NetworkX graph")
            raise

    def parse_json(self, links, nodes):
        """
        Build and return a NetworkX graph.

        :param dict links: dict of links between nodes
        :param dict nodes: dict of nodes in the network graph/topology
        :return bool True: True if NetworkX graph object created
        :rtype: bool
        """

        topo_json = {
            "directed": False,
            "multigraph": False,
            "nodes": nodes,
            "links": links,
        }

        # Create the node/edge graph from the JSON topology data:
        try:
            self.graph = nx.readwrite.json_graph.node_link_graph(topo_json)
        except Exception:
            print("Couldn't convert topology JSON data to NetworkX graph")
            raise
