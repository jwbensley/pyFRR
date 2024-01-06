import logging
import os

from .settings import Settings

logger = logging.getLogger(__name__)


class Logs:
    @staticmethod
    def setup() -> None:
        """
        Standardise logging output across all modules

        :rtype: None
        """
        os.makedirs(os.path.dirname(Settings.LOG_DIR), exist_ok=True)
        if Settings.DEV:
            logging.basicConfig(
                format=Settings.LOG_FORMAT_DEV,
                level=Settings.LOG_DEV_LEVEL,
                handlers=[
                    logging.FileHandler(
                        Settings.LOG_DIR, mode=Settings.LOG_MODE
                    ),
                    logging.StreamHandler(),
                ],
            )
        elif Settings.DEBUG:
            logging.basicConfig(
                format=Settings.LOG_FORMAT_DEBUG,
                level=logging.DEBUG,
                handlers=[
                    logging.FileHandler(
                        Settings.LOG_DIR, mode=Settings.LOG_MODE
                    ),
                    logging.StreamHandler(),
                ],
            )
        else:
            logging.basicConfig(
                format=Settings.LOG_FORMAT_INFO,
                level=logging.INFO,
                handlers=[
                    logging.FileHandler(
                        Settings.LOG_DIR, mode=Settings.LOG_MODE
                    ),
                    logging.StreamHandler(),
                ],
            )

        logging.info(
            f"Started logging to {Settings.LOG_DIR} at level "
            f"{logging.getLevelName(logging.getLogger().getEffectiveLevel())}"
        )
