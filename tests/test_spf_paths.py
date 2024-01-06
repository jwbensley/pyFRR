from __future__ import annotations

import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
)

from typing import Dict

import pytest
from fixtures import topo

from pypaths.path import NodePath, NodePaths
from pypaths.pypaths import PyPaths
from pypaths.topology import Topology


class TestSpfPaths:
    pp: PyPaths

    @pytest.fixture(scope="module")
    def test_data(self: TestSpfPaths) -> Dict:
        """
        This immutable fixture stores the expected results of unit tests
        """
        return {
            "no_paths": 94,
            "paths": {
                "PE1": {
                    "PE2": [
                        ['PE1', 'PE2'],
                    ],
                    "PE3": [
                        ['PE1', 'P1', 'P3', 'PE3'],
                    ],
                    "PE4": [
                        ['PE1', 'P1', 'P4', 'PE4'],
                        ['PE1', 'PE5', 'P4', 'PE4'],
                    ],
                    "PE5": [
                        ['PE1', 'PE5'],
                    ],
                    "P1": [
                        ['PE1', 'P1'],
                    ],
                    "P2": [
                        ['PE1', 'P1', 'P2'],
                        ['PE1', 'PE2', 'P2'],
                    ],
                    "P3": [
                        ['PE1', 'P1', 'P3'],
                    ],
                    "P4": [
                        ['PE1', 'P1', 'P4'],
                        ['PE1', 'PE5', 'P4'],
                    ],
                    "P5": [],
                },
                "PE2": {
                    "PE1": [
                        ['PE2', 'PE1'],
                    ],
                    "PE3": [
                        ['PE2', 'PE1', 'P1', 'P3', 'PE3'],
                        ['PE2', 'P2', 'P1', 'P3', 'PE3'],
                        ['PE2', 'P2', 'P4', 'P3', 'PE3'],
                    ],
                    "PE4": [
                        ['PE2', 'P2', 'P4', 'PE4'],
                    ],
                    "PE5": [
                        ['PE2', 'PE1', 'PE5'],
                    ],
                    "P1": [
                        ['PE2', 'PE1', 'P1'],
                        ['PE2', 'P2', 'P1'],
                    ],
                    "P2": [
                        ['PE2', 'P2'],
                    ],
                    "P3": [
                        ['PE2', 'PE1', 'P1', 'P3'],
                        ['PE2', 'P2', 'P1', 'P3'],
                        ['PE2', 'P2', 'P4', 'P3'],
                    ],
                    "P4": [
                        ['PE2', 'P2', 'P4'],
                    ],
                    "P5": [],
                },
                "PE3": {
                    "PE1": [
                        ['PE3', 'P3', 'P1', 'PE1'],
                    ],
                    "PE2": [
                        ['PE3', 'P3', 'P1', 'PE1', 'PE2'],
                        ['PE3', 'P3', 'P1', 'P2', 'PE2'],
                        ['PE3', 'P3', 'P4', 'P2', 'PE2'],
                    ],
                    "PE4": [
                        ['PE3', 'P3', 'P4', 'PE4'],
                    ],
                    "PE5": [
                        ['PE3', 'P3', 'P4', 'PE5'],
                    ],
                    "P1": [
                        ['PE3', 'P3', 'P1'],
                    ],
                    "P2": [
                        ['PE3', 'P3', 'P1', 'P2'],
                        ['PE3', 'P3', 'P4', 'P2'],
                    ],
                    "P3": [
                        ['PE3', 'P3'],
                    ],
                    "P4": [
                        ['PE3', 'P3', 'P4'],
                    ],
                    "P5": [],
                },
                "PE4": {
                    "PE1": [
                        ['PE4', 'P4', 'PE5', 'PE1'],
                        ['PE4', 'P4', 'P1', 'PE1'],
                    ],
                    "PE2": [
                        ['PE4', 'P4', 'P2', 'PE2'],
                    ],
                    "PE3": [
                        ['PE4', 'P4', 'P3', 'PE3'],
                    ],
                    "PE5": [
                        ['PE4', 'P4', 'PE5'],
                    ],
                    "P1": [
                        ['PE4', 'P4', 'P1'],
                    ],
                    "P2": [
                        ['PE4', 'P4', 'P2'],
                    ],
                    "P3": [
                        ['PE4', 'P4', 'P3'],
                    ],
                    "P4": [
                        ['PE4', 'P4'],
                    ],
                    "P5": [],
                },
                "PE5": {
                    "PE1": [
                        ['PE5', 'PE1'],
                    ],
                    "PE2": [
                        ['PE5', 'PE1', 'PE2'],
                    ],
                    "PE3": [
                        ['PE5', 'P4', 'P3', 'PE3'],
                    ],
                    "PE4": [
                        ['PE5', 'P4', 'PE4'],
                    ],
                    "P1": [
                        ['PE5', 'PE1', 'P1'],
                        ['PE5', 'P4', 'P1'],
                    ],
                    "P2": [
                        ['PE5', 'P4', 'P2'],
                    ],
                    "P3": [
                        ['PE5', 'P4', 'P3'],
                    ],
                    "P4": [
                        ['PE5', 'P4'],
                    ],
                    "P5": [],
                },
                "P1": {
                    "PE1": [
                        ['P1', 'PE1'],
                    ],
                    "PE2": [
                        ['P1', 'PE1', 'PE2'],
                        ['P1', 'P2', 'PE2'],
                    ],
                    "PE3": [
                        ['P1', 'P3', 'PE3'],
                    ],
                    "PE4": [
                        ['P1', 'P4', 'PE4'],
                    ],
                    "PE5": [
                        ['P1', 'PE1', 'PE5'],
                        ['P1', 'P4', 'PE5'],
                    ],
                    "P2": [
                        ['P1', 'P2'],
                    ],
                    "P3": [
                        ['P1', 'P3'],
                    ],
                    "P4": [
                        ['P1', 'P4'],
                    ],
                    "P5": [],
                },
                "P2": {
                    "PE1": [
                        ['P2', 'PE2', 'PE1'],
                        ['P2', 'P1', 'PE1'],
                    ],
                    "PE2": [
                        ['P2', 'PE2'],
                    ],
                    "PE3": [
                        ['P2', 'P1', 'P3', 'PE3'],
                        ['P2', 'P4', 'P3', 'PE3'],
                    ],
                    "PE4": [
                        ['P2', 'P4', 'PE4'],
                    ],
                    "PE5": [
                        ['P2', 'P4', 'PE5'],
                    ],
                    "P1": [
                        ['P2', 'P1'],
                    ],
                    "P3": [
                        ['P2', 'P1', 'P3'],
                        ['P2', 'P4', 'P3'],
                    ],
                    "P4": [
                        ['P2', 'P4'],
                    ],
                    "P5": [],
                },
                "P3": {
                    "PE1": [
                        ['P3', 'P1', 'PE1'],
                    ],
                    "PE2": [
                        ['P3', 'P1', 'PE1', 'PE2'],
                        ['P3', 'P1', 'P2', 'PE2'],
                        ['P3', 'P4', 'P2', 'PE2'],
                    ],
                    "PE3": [
                        ['P3', 'PE3'],
                    ],
                    "PE4": [
                        ['P3', 'P4', 'PE4'],
                    ],
                    "PE5": [
                        ['P3', 'P4', 'PE5'],
                    ],
                    "P1": [
                        ['P3', 'P1'],
                    ],
                    "P2": [
                        ['P3', 'P1', 'P2'],
                        ['P3', 'P4', 'P2'],
                    ],
                    "P4": [
                        ['P3', 'P4'],
                    ],
                    "P5": [],
                },
                "P4": {
                    "PE1": [
                        ['P4', 'PE5', 'PE1'],
                        ['P4', 'P1', 'PE1'],
                    ],
                    "PE2": [
                        ['P4', 'P2', 'PE2'],
                    ],
                    "PE3": [
                        ['P4', 'P3', 'PE3'],
                    ],
                    "PE4": [
                        ['P4', 'PE4'],
                    ],
                    "PE5": [
                        ['P4', 'PE5'],
                    ],
                    "P1": [
                        ['P4', 'P1'],
                    ],
                    "P2": [
                        ['P4', 'P2'],
                    ],
                    "P3": [
                        ['P4', 'P3'],
                    ],
                    "P5": [],
                },
                "P5": {
                    "PE1": [],
                    "PE2": [],
                    "PE3": [],
                    "PE4": [],
                    "PE5": [],
                    "P1": [],
                    "P2": [],
                    "P3": [],
                    "P4": [],
                },
            },
        }

    @classmethod
    def setup_class(cls) -> None:
        TestSpfPaths.pp = PyPaths(Topology.from_json_file(topo["filename"]))

    def test_spf(self: TestSpfPaths, test_data: Dict) -> None:
        assert len(TestSpfPaths.pp.spf_paths) == test_data["no_paths"]
        for source in TestSpfPaths.pp.topology.get_nodes_list():
            for target in TestSpfPaths.pp.topology.get_nodes_list():
                if source == target:
                    continue
                paths: NodePaths = TestSpfPaths.pp.spf_paths.get_paths_between(
                    source, target
                )
                path: NodePath
                for path in paths:
                    assert [str(node) for node in path] in test_data["paths"][
                        str(source)
                    ][str(target)]
