import logging
import os
from logging.handlers import RotatingFileHandler


LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILENAME = os.path.join(LOG_DIR, "nfc_available_rest.log")


def configure_logging(level: int = logging.INFO, max_bytes: int = 5_000_000, backup_count: int = 5) -> None:
    """Configure le logging avec un RotatingFileHandler et la sortie console.

    - `LOG_DIR` (env) peut être utilisé pour changer l'emplacement des logs.
    - `max_bytes` et `backup_count` contrôlent la rotation.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Formatters
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # Rotating file handler
    file_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Clear existing handlers to avoid duplicate logs in some environments
    if root_logger.handlers:
        root_logger.handlers = []

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


if __name__ == "__main__":
    configure_logging()
