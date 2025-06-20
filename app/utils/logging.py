import logging
import os

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level.upper())
        file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_format)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level.upper())
        console_handler.setFormatter(file_format)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
