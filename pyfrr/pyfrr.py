from __future__ import annotations

from .all_paths import AllPaths
from .log import Logger
from .spf import Spf
from .topology import Topology


class PyFrr:
    def __init__(self: PyFrr, filename: str = "") -> None:
        Logger.setup()
        if filename:
            self.topology: Topology = Topology.from_nx_json_file(filename)
            self.all_paths: AllPaths = AllPaths(self.topology)
            self.spf_paths: Spf = Spf(
                all_paths=self.all_paths, topology=self.topology
            )

            print(
                "All paths between PE1 and PE4:\n"
                f"{self.all_paths.get_paths_between_by_name('PE1', 'PE4')}"
            )
            print(
                "Lowest weighted paths between PE1 and PE4:\n"
                f"{self.spf_paths.get_paths_between_by_name('PE1', 'PE4')}"
            )
