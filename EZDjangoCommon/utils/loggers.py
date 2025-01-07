import sys
from loguru import logger

logger.add(
    sys.stderr,
    format="<green>{time}</green> {level} {message}",
    filter="my_module",
    level="INFO",
    colorize=True,
)
