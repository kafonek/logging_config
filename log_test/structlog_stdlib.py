import logging
import time

logger = logging.getLogger(__name__)


async def divide(x, y):
    """
    Show vanilla logging output in an async function.
     - highlight slow async tasks using time.sleep(1)
     - highlight logged exceptions with extras
    """
    logger.debug(f"DIVIDING {x} / {y}")
    logger.info(f"DIVIDING {x} / {y}")
    logger.warn(f"DIVIDING {x} / {y}")
    try:
        x / 0
    except Exception as e:
        logger.exception(e, extra={"x": x})
    time.sleep(1)
    return x / y
