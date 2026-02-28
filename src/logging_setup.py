import sys
from loguru import logger


def setup_logging() -> None:
    """
    Configure application logging.

    We avoid print() for anything meaningful; logs are essential later for:
    - API error debugging
    - guardrails decisions
    - prompt strategy comparisons
    """
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
    )