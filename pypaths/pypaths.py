from __future__ import annotations

import logging

from .all_paths import AllPaths
from .lfa_paths import LfaPaths
from .logs import Logs
from .rlfa_paths import RlfaPaths
from .spf_paths import SpfPaths
from .topology import Topology

logger = logging.getLogger(__name__)


class PyPaths:
    def __init__(self: PyPaths, topology: Topology) -> None:
        Logs.setup()
        self.topology: Topology = topology
        self.all_paths: AllPaths = AllPaths(self.topology)
        self.spf_paths: SpfPaths = SpfPaths(
            all_paths=self.all_paths, topology=self.topology
        )
        self.lfa_paths: LfaPaths = LfaPaths(
            spf_paths=self.spf_paths, topology=self.topology
        )
        self.rlfa_paths: RlfaPaths = RlfaPaths(
            spf_paths=self.spf_paths, topology=self.topology
        )
