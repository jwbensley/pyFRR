import os
from diagram import diagram


class base:
    """This class provides functions for the base (unmodified) topology"""

    def __init__(self, debug: bool = 0):
        """
        Init the Base class.

        :param int debug: debug level, 0 is disabled.
        :return None: __init__ shouldn't return anything
        :rtype: None
        """

        self.debug = debug
        self.diagram = diagram(debug=self.debug)
        self.path_types = ["base"]

    def draw(self, graph, outdir, topology):
        """
        Render the base topology diagram (the loaded topology with nothing
        highlighted).

        :param networkx.Graph graph: NetworkX graph object
        :param str outdir: string of the root output directory path
        :param dict topology: topology paths dict
        :return bool True: True if diagram rendered otherwise False
        :rtype: bool
        """

        self.diagram.gen_sub_dirs(graph, outdir, self.path_types, topology)

        # Add labels to links showing their cost
        base_graph = graph.copy()
        base_graph = self.diagram.label_link_weights(base_graph)

        self.diagram.gen_diagram("base", base_graph, os.path.join(outdir, "base"))

        return


    def init_topo(self, graph, topo):
        """
        Create empty dict keys for all possible paths.

        :return None:
        :rtype: None
        """

        for src in graph.nodes:
            if src not in topo:
                topo[src] = {}

            for dst in graph.nodes:
                if src == dst:
                    continue

                if dst not in topo[src]:
                    topo[src][dst] = {}
