import unittest

import networkx as nx
import os
import sys
sys.path.append('./')
from base import base
from spf import spf

class TestSPF(unittest.TestCase):

    b = base(debug=1)
    ######d = diagram(debug=1)
    s = spf(debug=1)

    outdir = "/tmp/pyFRR_tests"
    g = nx.Graph()
    g.add_node(4)
    g.add_edges_from([(1,2), (2,3), (3,4), (4,1)])
    topo = {}
    b.init_topo(g, topo)

    def test_init_topo(self):
        self.assertEqual(
            None, self.s.init_topo(self.g, self.topo)
        )
        for src in self.g.nodes:
            for dst in self.g.nodes:
                if src == dst:
                    continue

                for path_type in self.s.path_types:
                    self.assertTrue(path_type in self.topo[src][dst])
                    self.assertTrue(isinstance(self.topo[src][dst][path_type], list))

    def test_gen_metric_cost(self):
        g2 = self.g.copy()
        cost = self.s.gen_metric_cost(1, g2, 2)
        self.assertTrue(isinstance(cost, int))
        self.assertEqual(1, cost)
        # Force traffic the other way around the ring
        g2.edges[(1,2)]["weight"] = 10
        cost = self.s.gen_metric_cost(1, g2, 2)
        self.assertTrue(isinstance(cost, int))
        self.assertEqual(3, cost)

    def test_gen_metric_paths(self):
        paths = self.s.gen_metric_paths(1, self.g, 3)
        self.assertTrue(isinstance(paths, list))
        self.assertEqual(paths, [[3, 2, 1], [3, 4, 1]])

    def test_gen_nei_metric_paths(self):
        paths = self.s.gen_nei_metric_paths(1, self.g, 3)
        self.assertTrue(isinstance(paths, dict))
        self.assertTrue(isinstance(paths[1], dict))
        self.assertTrue(isinstance(paths[1][2], list))
        self.assertEqual(paths[1][2], [[2, 1]])
        self.assertTrue(isinstance(paths[1][4], list))
        self.assertEqual(paths[1][4], [[4, 1]])
        self.assertTrue(isinstance(paths[3], dict))
        self.assertTrue(isinstance(paths[3][2], list))
        self.assertEqual(paths[3][2], [[3, 2]])
        self.assertTrue(isinstance(paths[3][4], list))
        self.assertEqual(paths[3][4], [[3, 4]])

    def test_gen_path_cost(self):
        with self.assertRaises(KeyError):
            self.s.gen_path_cost(self.g, [1,2,3,4,1])
        g2 = self.g.copy()
        for edge in g2.edges:
            g2.edges[edge]["weight"] = 2
        cost = self.s.gen_path_cost(g2, [1,2,3,4,1])
        self.assertTrue(isinstance(cost, int))
        self.assertEqual(cost, 8)

if __name__ == '__main__':
    unittest.main()