import logging

logger = logging.getLogger(__name__)


def add(x, y):
    """
    Show vanilla logging output in a sync function.
     - highlight using extra
    """
    logger.debug(f"ADDING {x} + {y}")
    logger.info(f"ADDING {x} + {y}", extra={"for": "eli"})
    logger.warn(f"ADDING {x} + {y}")

    return x + y
