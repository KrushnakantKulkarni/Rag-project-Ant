import logging
import sys

# Configure standard structured logger format
log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance with the specified name.
    """
    return logging.getLogger(name)

# Expose global logger instance for general use
logger = get_logger("failure-forensics")
