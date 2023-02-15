from .all_paths import AllPaths
from .log import Logger

# from .spf import Spf
from .topology import Topology


class PyFrr:
    topology: Topology
    all_paths: AllPaths
    # spf: Spf

    def __init__(self, filename: str = "") -> None:
        Logger.setup()
        if filename:
            self.topology = Topology.from_nx_json_file(filename)
            self.all_paths = AllPaths(self.topology)
