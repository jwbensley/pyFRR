from .all_paths import AllPaths
from .log import Logger
#from .spf import Spf
from .topology import Topology


class PyFrr:
    topology: Topology = Topology()
    all_paths: AllPaths
    #spf: Spf

    def __init__(self) -> None:
        Logger.setup()

    def load_nx_json(self, filename: str) -> None:
        self.topology.from_nx_json_file(filename)
        self.all_paths = AllPaths(self.topology)
        # self.spf = Spf(self.topology)
