import structlog

logger = structlog.get_logger(__name__)


def multiply(x, y):
    """
    Show structlog output in a sync function.
    - highlight logged exceptions with extras
    """
    logger.debug(f"MULTIPLYING {x} * {y}")
    logger.info(f"MULTIPLYING {x} * {y}")
    logger.warn(f"MULTIPLYING {x} * {y}")
    try:
        x + "foo"
    except Exception as e:
        logger.exception(e, x=x)
    return x * y
