import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
)

from pyfrr.topology import Topology
import json
from typing import Dict


class TestTopology:
    input_topology_file: str = "examples/mesh/mesh.json"
    output_topology_file: str = "tests/mesh-test.json"
    test_topology: Topology

    def test_from_nx_json_file(self) -> None:
        self.test_topology = Topology.from_nx_json_file(
            self.input_topology_file
        )
        assert self.test_topology.no_of_edges() == 28
        assert self.test_topology.no_of_nodes() == 10

    def test_to_nx_json_file(self) -> None:
        self.test_topology = Topology.from_nx_json_file(
            self.input_topology_file
        )
        self.test_topology.to_nx_json_file(
            self.output_topology_file, self.test_topology
        )
        reference_data: Dict = json.load(open(self.input_topology_file))
        test_data: Dict = json.load(open(self.output_topology_file))
        """
        Because the NetworkX style JSON exports store links and nodes in
        unsorted lists, we have to loop over the lists to find if entries
        exist, we can't compare them directly:
        """
        for link in reference_data["links"]:
            if link in test_data["links"]:
                test_data["links"].remove(link)
        for node in reference_data["nodes"]:
            if node in test_data["nodes"]:
                test_data["nodes"].remove(node)
        assert not test_data["links"]
        assert not test_data["nodes"]
