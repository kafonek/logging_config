import asyncio

import structlog
from ddtrace import tracer

from log_test.log_stuff import add
from log_test.structlog_stdlib import divide
from log_test.structlog_stuff import multiply


@tracer.wrap(name="run func", service="demo service")
async def run():
    # add kwarg "contextfoo=bar" to all log messages
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(contextfoo="bar")
    # "adding" is sync,  uses vanilla logging
    print(f"Adding: {add(2, 3)=}")
    # "multiplying" is sync, uses structlog
    print(f"Multiplying: {multiply(2, 3)=}")
    # "dividing" is async, uses vanilla logging
    div = await divide(2, 3)
    print(f"Dividing: {div=}")


if __name__ == "__main__":
    from log_test.logging_utils import configure_logging

    configure_logging()
    asyncio.run(run())
