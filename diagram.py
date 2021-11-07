import networkx as nx
import os
import shlex
import subprocess

##from networkx.drawing.nx_pydot import write_dot


class diagram:
    """
    A class for generating diagrams from the passed topology graph.
    """

    def __init__(self, debug: bool = 0):
        """
        Init the Diagram class.

        :param int debug: debug level, 0 is disabled.
        :return: None, __init__ shouldn't return anything
        :rtype: None
        """
        self.debug = debug

    def gen_diagram(self, filename, graph, outdir):
        """
        Generate the topology diagram based upon the networkX graph topology.

        :param str filename: basename of output filename
        :param networkx.Graph graph: NetworkX graph object
        :param str outdir: string of the root output directory path
        :return bool: True or False result of diagram rendering
        :rtype: bool
        """

        node_dot = os.path.join(outdir, filename + ".dot")
        node_png = os.path.join(outdir, filename + ".png")

        """
        If the overlap mode is "scale" the layout is uniformly scaled up,
        preserving node sizes, until nodes no longer overlap.
        The default overlap mode is "true", meaning no repositioning is done.
        """
        dot = nx.nx_pydot.to_pydot(graph)
        dot.set_overlap("scale")
        graph = nx.nx_pydot.from_pydot(dot)
        try:
            nx.drawing.nx_pydot.write_dot(graph, node_dot)
        except Exception:
            print(f"Failed to write dot file {node_dot}")
            raise

        """
        CLI Args:
        nodesep= sets the minimum separation between nodes.
        ranksep= sets the minimum separation between ranks.
        
        Without Nwidth and Nheight the nodes auto scale to the size of their
        label text. Nwidth and Nheight only set a minimum size though.
        If the text is larger than this minimum size, the node will still scale
        up, meaning inconsistent node sizes for some nodes with longer names.
        Nfixedsize=true forces nodes to be the actual size (text label length
        is ignored).
        """
        cmd = (
            "fdp -Gsize=100,100 -Gdpi=100 -Gnodesep=equally -Granksep=equally "
            "-Nshape=circle -Nstyle=filled -Nwidth=2 -Nheight=2 "
            f"-Nfixedsize=true -Tpng -o {shlex.quote(node_png)} "
            f"{shlex.quote(node_dot)}"
        )

        result = subprocess.getstatusoutput(cmd)
        if result[0] != 0:
            raise Exception(
                f"Error rendering diagram with fdp, "
                f"have you installed graphviz?\n"
                f"{result[1]}"
            )

        cmd = "rm -f " + shlex.quote(node_dot)

        result = subprocess.getstatusoutput(cmd)
        if result[0] != 0:
            raise Exception(
                f"Error deleting pydot dot file {node_dot}: {result[1]}"
            )

    def gen_root_dir(self, outdir: str) -> None:
        """
        Creates the output base directory for rendered diagrams.

        :param str outdir: base directory for ourput folder hierarchy
        :return: None, raise if fail
        :rtype: None
        """

        if os.path.isdir(outdir):
            if self.debug > 0:
                print(f"Diagram output directory ({outdir}) already exists")

        else:
            try:
                os.makedirs(outdir, exist_ok=True)
            except Exception:
                print(
                    f"Couldn't create diagram output directory {outdir}"
                )
                raise

    def gen_sub_dirs(self, graph: nx.classes.graph.Graph, outdir: str, path_types: list, topology: dict) -> None:
        """
        Create the sub-directories under the root outdir that digrams will be
        rendered to as files.

        :param networkx.Graph graph: NetworkX graph object
        :param str outdir: root output directory
        :param list path_types: list of str. Path types in topology to render
        :param dict topology: topology paths dict
        :return: None, raise if fail
        :rtype: None
        """

        # A special case
        if "base" in path_types:
            try:
                base_dir = os.path.join(outdir, "base")
                os.makedirs(base_dir, exist_ok=True)
            except Exception:
                print(
                    f"Couldn't create base toplogy diagram directory {base_dir}"
                )
                raise
            path_types.remove("base")
        
        if path_types == []:
            return

        for src in graph.nodes:
            if src in topology:
                try:
                    src_dir = os.path.join(outdir, str(src))
                    os.makedirs(src_dir, exist_ok=True)
                    for dst in topology[src]:
                        for path_type in path_types:
                            if len(topology[src][dst][path_type]) > 0:
                                frr_dir = os.path.join(src_dir, path_type)
                                os.makedirs(frr_dir, exist_ok=True)

                except Exception:
                    print(f"Couldn't create node directory {src_dir}")
                    raise

    def highlight_fh_link(self, colour: str, graph: nx.classes.graph.Graph, path: list) -> nx.classes.graph.Graph:
        """
        Highlight the first-hop link "colour" in path.
        If "colour" is None, remove any exisiting colour.

        :param str colour: string name of dot colour
        :param networkx.Graph graph: NetworkX graph object
        :param list path: List of nodes from src to dst
        :return networkx.Graph tmp_g: "graph" copy with colour attributes added
        :rtype: networkx.Graph
        """

        tmp_g = graph.copy()

        # Set the first-hop links on all paths to "colour"
        if colour:
            tmp_g.edges[path[0], path[1]]["color"] = colour
            tmp_g.edges[path[0], path[1]]["penwidth"] = "10.0"
        else:
            del tmp_g.edges[path[0], path[1]]["color"]
            del tmp_g.edges[path[0], path[1]]["penwidth"]

        return tmp_g

    def highlight_fh_node(self, colour: str, graph: nx.classes.graph.Graph, path: list) -> nx.classes.graph.Graph:
        """
        Highlight the first-hop node "colour" in "path".
        If "colour" is None, remove any exisiting colour.

        :param str colour: string name of dot colour
        :param networkx.Graph graph: NetworkX graph object
        :param list path: List of nodes in path
        :return networkx.Graph tmp_g: "graph" copy with colour attributes added
        :rtype: networkx.Graph
        """

        tmp_g = graph.copy()

        # Set the first-hop node in "path" to "colour"
        if colour:
            tmp_g.nodes[path[1]]["fillcolor"] = colour
        else:
            del tmp_g.nodes[path[1]]["fillcolor"]

        return tmp_g

    def highlight_links(self, colour: str, graph: nx.classes.graph.Graph, path: list) -> nx.classes.graph.Graph:
        """
        Highlight the links/edges along the path stored in "path" as "colour".
        If "colour" is None remove any exisiting colour.

        :param str colour: string name of dot colour
        :param networkx.Graph graph: NetworkX graph object
        :param list path: List of nodes in path
        :return networkx.Graph tmp_g: "graph" copy with colour attributes added
        :rtype: networkx.Graph
        """

        tmp_g = graph.copy()

        # Highlight the links(s) along "path" with "colour".
        for idx, node in enumerate(path):
            if idx < (len(path) - 1):
                if colour:
                    tmp_g.edges[node, path[idx + 1]]["color"] = colour
                    tmp_g.edges[node, path[idx + 1]]["penwidth"] = "10.0"
                else:
                    del tmp_g.edges[node, path[idx + 1]]["color"]
                    del tmp_g.edges[node, path[idx + 1]]["penwidth"]

        return tmp_g

    def highlight_nodes(self, colour: str, graph: nx.classes.graph.Graph, path: list) -> nx.classes.graph.Graph:
        """
        Highlight nodes "colour" along "path".
        If "colour" is None remove any exisiting colour.

        :param str colour: string name of dot colour
        :param networkx.Graph graph: NetworkX graph object
        :param list path: List of nodes in path
        :return networkx.Graph tmp_g: "graph" copy with colour attributes added
        :rtype: networkx.Graph
        """

        tmp_g = graph.copy()

        # Highlight the nodes(s) along "path" wiith "colour".
        for idx, node in enumerate(path):
            if colour:
                tmp_g.nodes[node]["fillcolor"] = colour
            else:
                del tmp_g.nodes[node]["fillcolor"]

        return tmp_g

    def highlight_src_dst(self, colour: str, dst: str, graph: nx.classes.graph.Graph, src: str) -> nx.classes.graph.Graph:
        """
        Highlight the "src" and "dst" nodes in "graph" "colour". If "colour" is
        None, remove any exisiting colour.

        :param str colour: string name of dot colour
        :param str dst: string name of destination node in "graph"
        :param networkx.Graph graph: NetworkX graph object
        :param str src: string name of source node in "graph"
        :return networkx.Graph tmp_g: "graph" copy with colour attributes added
        :rtype: networkx.Graph
        """

        tmp_g = graph.copy()

        # Highlight the source node and destination nodes.
        if colour:
            tmp_g.nodes[src]["fillcolor"] = colour
            tmp_g.nodes[dst]["fillcolor"] = colour
        else:
            del tmp_g.nodes[src]["fillcolor"]
            del tmp_g.nodes[dst]["fillcolor"]

        return tmp_g

    def label_link_add_adjsid(self, graph: nx.classes.graph.Graph) -> nx.classes.graph.Graph:
        """
        Add the SR Adj-SID for each edge/link to it's existing label.

        :param networkx.Graph graph: NetworkX graph object
        :return networkx.Graph tmp_g: "graph" copy with edge labels added
        :rtype: networkx.Graph
        """
        tmp_g = graph.copy()

        for edge in graph.edges():
            if "adj_sid" not in tmp_g.edges[edge[0], edge[1]]:
                continue
            if "label" not in tmp_g.edges[edge[0], edge[1]]:
                tmp_g.edges[edge[0], edge[1]]["label"] = ""
            tmp_g.edges[edge[0], edge[1]]["label"] += (
                "\n" + str(tmp_g.edges[edge[0], edge[1]]["adj_sid"])
            )

        return tmp_g

    def label_link_weights(self, graph: nx.classes.graph.Graph) -> nx.classes.graph.Graph:
        """
        Add a label to each edge/link which is the weight of that link.

        :param networkx.Graph graph: NetworkX graph object
        :return networkx.Graph tmp_g: "graph" copy with edge labels added
        :rtype: networkx.Graph
        """
        tmp_g = graph.copy()

        for edge in graph.edges():
            if "weight" in tmp_g.edges[edge[0], edge[1]]:
                tmp_g.edges[edge[0], edge[1]]["label"] = str(
                    tmp_g.edges[edge[0], edge[1]]["weight"]
                )

        return tmp_g

    def label_node_id(self, graph: nx.classes.graph.Graph) -> nx.classes.graph.Graph:
        """
        Add a label to each node which is its ID.

        :param networkx.Graph graph: NetworkX graph object
        :return networkx.Graph tmp_g: "graph" copy with edge labels added
        :rtype: networkx.Graph
        """
        tmp_g = graph.copy()

        for node in graph.nodes:
            tmp_g.nodes[node]["label"] = str(node)

        return tmp_g

    def label_node_add_nodesid(self, graph: nx.classes.graph.Graph) -> nx.classes.graph.Graph:
        """
        Add a label to each node which is its ID.

        :param networkx.Graph graph: NetworkX graph object
        :return networkx.Graph tmp_g: "graph" copy with edge labels added
        :rtype: networkx.Graph
        """
        tmp_g = graph.copy()

        for node in graph.nodes:
            if "node_sid" not in tmp_g.nodes[node]:
                continue
            if "label" not in tmp_g.nodes[node]:
                tmp_g.nodes[node]["label"] = ""
            tmp_g.nodes[node]["label"] += (
                "\n" + str(tmp_g.nodes[node]["node_sid"])
            )

        return tmp_g
