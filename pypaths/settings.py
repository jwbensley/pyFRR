import os
import sys
import typing


class Settings:
    #
    # GENERAL
    #

    BASE_DIR: str = os.path.dirname(os.path.realpath(__file__))
    # Run in debug mode, which is more verbose than normal
    DEBUG: bool = False
    # Run in dev mode, a firehorse of information
    DEV: bool = False

    #
    # LOGGING
    #

    # Log mode, 'a'ppend or over'w'rite
    LOG_MODE: str = "a"

    # Standard logging format
    LOG_FORMAT_INFO: str = "%(asctime)s|%(levelname)s|%(message)s"

    # Debugging logging formart
    LOG_FORMAT_DEBUG: str = (
        "%(asctime)s|%(levelname)s|%(process)d|%(funcName)s|%(message)s"
    )

    # Dev logging format
    LOG_FORMAT_DEV: str = (
        "%(asctime)s|%(levelname)s|%(process)d|%(funcName)s|%(lineno)d|"
        "%(message)s"
    )

    # Dev logging level - custom logging level for more granularity
    LOG_DEV_LEVEL: int = 5

    # Logging levels
    LOG_INFO = "info"
    LOG_DEBUG = "debug"
    LOG_DEV = "dev"

    # Log file
    LOG_DIR: str = os.path.join(BASE_DIR, "pypaths.log")

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
