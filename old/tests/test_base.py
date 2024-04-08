import unittest

import networkx as nx
import os
import sys
sys.path.append('./')
from base import base

class TestBase(unittest.TestCase):

    b = base(debug=1)

    outdir = "/tmp/pyFRR_tests"
    g = nx.Graph()
    g.add_node(4)
    g.add_edges_from([(1,2), (2,3), (3,4), (4,1)])
    topo = {}

    def test_init_topo(self):
        self.assertEqual(
            None, self.b.init_topo(self.g, self.topo)
        )
        for src in self.g.nodes:
            for dst in self.g.nodes:
                if src == dst:
                    continue
                self.assertTrue(isinstance(self.topo[src][dst], dict))

    def test_draw(self):
        self.b.draw(self.g, self.outdir, self.topo)
        outdir = self.outdir + "/base"
        self.assertTrue(os.path.isdir(outdir))
        outfile = outdir + "/base.png"
        self.assertTrue(os.path.isfile(outfile))

if __name__ == '__main__':
    unittest.main()