import os
import sys
import typing


class Settings:
    #
    # GENERAL
    #

    BASE_DIR: str = os.path.dirname(os.path.realpath(__file__))
    DEBUG = False

    #
    # LOGGING
    #

    # Log mode, 'a'ppend or over'w'rite
    LOG_MODE = "a"

    # Standard logging format
    LOG_STANDARD: str = "%(asctime)s|%(levelname)s|%(message)s"

    # Debugging logging formart
    LOG_DEBUG: str = (
        "%(asctime)s|%(levelname)s|%(process)d|%(funcName)s|%(message)s"
    )

    # Log file
    LOG_DIR = os.path.join(BASE_DIR, "pyfrr.log")

    #
    # Graph Settings
    #

    # Name of the weight key/value when loading from JSON
    EDGE_WEIGHT_KEY: str = "weight"

    # Default edge weight when none is set
    DEFAULT_WEIGHT: int = 0

    # Highest possible weight value
    HEIGHTEST_WEIGHT: int = sys.maxsize

    # Invalid weight value, when a weight is not found
    INVALID_WEIGHT: int = -1
