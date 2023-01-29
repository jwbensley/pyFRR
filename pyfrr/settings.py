import os
import sys
import typing


class Settings:
    #
    # GENERAL
    #

    BASE_DIR: str = os.path.dirname(os.path.realpath(__file__))
    DEBUG = True

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

    # Name of the weight field on a graph edge
    EDGE_WEIGHT: str = "weight"
