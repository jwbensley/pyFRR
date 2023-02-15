import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
)

from pyfrr.pyfrr import PyFrr
import typing


class TestAllPaths:
    input_topology_file: str = "examples/mesh.json"
    test_network: PyFrr = PyFrr(input_topology_file)

    def test_all_paths(self):
        assert len(self.test_network.all_paths) == 542
