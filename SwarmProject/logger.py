import logging
from config import LOG_FILE

def setup_logger():
    logger = logging.getLogger("SWED-A")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        
        # Output strictly to file to keep console output clean for custom formats
        fh = logging.FileHandler(LOG_FILE)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

logger = setup_logger()
