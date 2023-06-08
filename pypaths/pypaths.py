from __future__ import annotations

from .all_paths import AllPaths
from .log import Logger
from .spf import Spf
from .topology import Topology


class PyPaths:
    def __init__(self: PyPaths, topology: Topology) -> None:
        Logger.setup()
        self.topology: Topology = topology
        self.all_paths: AllPaths = AllPaths(self.topology)
        self.spf_paths: Spf = Spf(
            all_paths=self.all_paths, topology=self.topology
        )
