from __future__ import annotations

import os
import sys

import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
)

import json
from typing import Dict, List

from fixtures import topo

from pypaths.topology import Topology


class TestTopology:
    @pytest.fixture(scope="module")
    def test_file(self: TestTopology) -> Dict:
        """
        This immutable fixture stores the expected results of unit tests
        """
        return {
            "filename": "tests/mesh-test.json",
        }

    def test_from_json_file(self: TestTopology) -> None:
        topology: Topology = Topology.from_json_file(topo["filename"])
        assert topology.no_of_edges() == topo["no_of_edges"]
        assert topology.no_of_nodes() == topo["no_of_nodes"]
        assert topology.get_node_names() == topo["nodes"]

    def test_to_json_file(self: TestTopology, test_file: Dict) -> None:
        topology = Topology.from_json_file(topo["filename"])
        topology.to_json_file(test_file["filename"], topology)

        topo_data: Dict[str, List[Dict]] = json.load(open(topo["filename"]))
        test_data: Dict[str, List[Dict]] = json.load(
            open(test_file["filename"])
        )
        """
        Because the JSON export store links and nodes in unsorted lists,
        we have to loop over the lists to find if all entries
        exist, we can't compare them directly:
        """
        for link in topo_data["links"]:
            if link in test_data["links"]:
                test_data["links"].remove(link)
        for node in topo_data["nodes"]:
            if node in test_data["nodes"]:
                test_data["nodes"].remove(node)
        assert not test_data["links"]
        assert not test_data["nodes"]
        os.unlink(test_file["filename"])
