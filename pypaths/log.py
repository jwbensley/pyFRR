import logging
import os

from .settings import Settings


class Logger:
    @staticmethod
    def setup() -> None:
        """
        Standardise logging output across all modules

        :rtype: None
        """
        os.makedirs(os.path.dirname(Settings.LOG_DIR), exist_ok=True)
        if Settings.DEBUG:
            logging.basicConfig(
                format=Settings.LOG_DEBUG,
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
                format=Settings.LOG_STANDARD,
                level=logging.INFO,
                handlers=[
                    logging.FileHandler(
                        Settings.LOG_DIR, mode=Settings.LOG_MODE
                    ),
                    logging.StreamHandler(),
                ],
            )

        logging.info(
            f"Starting logging to {Settings.LOG_DIR} at level "
            f"{logging.getLevelName(logging.getLogger().getEffectiveLevel())}"
        )
