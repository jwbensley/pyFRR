import unittest

import networkx as nx
import os
import sys
sys.path.append('./')
from base import base
from diagram import diagram
from spf import spf

class TestDiagram(unittest.TestCase):

    b = base(debug=1)
    d = diagram(debug=1)
    s = spf(debug=1)

    outdir = "/tmp/pyFRR_tests"
    g = nx.Graph()
    g.add_node(4)
    g.add_edges_from([(1,2), (2,3), (3,4), (4,1)])
    g.edges[1,2]["adj_sid"] = "123"
    g.edges[1,2]["weight"] = "123"
    g.nodes[1]["node_sid"] = "1"
    topo = {}
    b.init_topo(g, topo)
    s.init_topo(g, topo)
    topo[1][2]["spf_metric"] = list(nx.all_shortest_paths(g, source=1, target=2))

    def test_gen_root_dir(self):
        self.assertEqual(
            None, self.d.gen_root_dir(self.outdir)
        )
        self.assertTrue(os.path.isdir(self.outdir))

    def test_gen_sub_dirs(self):
        self.assertEqual(
            None, self.d.gen_sub_dirs(
                self.g, self.outdir, ["base"], self.topo
            )
        )
        self.assertEqual(
            None, self.d.gen_sub_dirs(
                self.g, self.outdir, ["base", "spf_metric"], self.topo
            )
        )
        outdir = self.outdir + "/base"
        self.assertTrue(os.path.isdir(outdir))

    def test_highlight_fh_link(self):
        g2 = self.d.highlight_fh_link("red", self.g, [1, 2, 3])
        self.assertEqual(g2.edges[(1,2)]["color"],"red")
        g2 = self.d.highlight_fh_link(None, g2, [1, 2, 3])
        self.assertTrue("color" not in g2.edges[(1,2)])

    def test_highlight_fh_node(self):
        g2 = self.d.highlight_fh_node("red", self.g, [1, 2, 3])
        self.assertEqual(g2.nodes[2]["fillcolor"],"red")
        g2 = self.d.highlight_fh_node(None, g2, [1, 2, 3])
        self.assertTrue("fillcolor" not in g2.nodes[2])

    def test_highlight_links(self):
        g2 = self.d.highlight_links("red", self.g, [1, 2, 3])
        self.assertEqual(g2.edges[(2, 3)]["color"],"red")
        g2 = self.d.highlight_links(None, g2, [1, 2, 3])
        self.assertTrue("color" not in g2.edges[(2, 3)])

    def test_highlight_nodes(self):
        g2 = self.d.highlight_nodes("red", self.g, [1, 2, 3])
        self.assertEqual(g2.nodes[2]["fillcolor"],"red")
        g2 = self.d.highlight_nodes(None, g2, [1, 2, 3])
        self.assertTrue("fillcolor" not in g2.nodes[2])

    def test_highlight_src_dst(self):
        g2 = self.d.highlight_src_dst("red", 2, self.g, 1)
        self.assertEqual(g2.nodes[1]["fillcolor"],"red")
        self.assertEqual(g2.nodes[2]["fillcolor"],"red")
        g2 = self.d.highlight_src_dst(None,  2, g2, 1)
        self.assertTrue("fillcolor" not in g2.nodes[1])
        self.assertTrue("fillcolor" not in g2.nodes[2])

    def test_label_link_add_adjsid(self):
        g2 = self.d.label_link_add_adjsid(self.g)
        self.assertEqual(
            g2.edges[(1,2)]["label"], "\n" + self.g.edges[(1,2)]["adj_sid"]
        )

    def test_label_link_weights(self):
        g2 = self.d.label_link_weights(self.g)
        self.assertEqual(
            g2.edges[(1,2)]["label"], self.g.edges[1,2]["weight"]
        )


    def test_label_node_id(self):
        g2 = self.d.label_node_id(self.g)
        self.assertEqual(
            g2.nodes[1]["label"], "1"
        )

    def test_label_node_add_nodesid(self):
        g2 = self.d.label_node_add_nodesid(self.g)
        self.assertEqual(
            g2.nodes[1]["label"], "\n1"
        )

if __name__ == '__main__':
    unittest.main()