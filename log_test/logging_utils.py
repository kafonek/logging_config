"""
Example of how to render both structlog and vanilla logging output using
a shared set of structlog-offered processors and logging.config.

See https://www.structlog.org/en/stable/standard-library.html for
more details, particularly the bottom section.

At a high level, what is being demonstrated here is that both structlog 
and vanilla loggers (`structlog.get_logger()` and `logging.getLogger()`)
will have their event dicts processed by the vanilla logging config, using
processors provided by the structlog library. 

There is a small amount of pre-processing that needs to be done to vanilla
log messages, which is usually tagged as pre_chain or foreign_pre_chain.

stuctlog messages also need some pre-processing to prepare them to be handed
over to the vanilla Formatter. Once vanilla logs and structlog messages are
both pre-processed, then a set of shared processors can be applied in the
vanilla logging config formatters -> processors section.
"""

import logging
import logging.config

import aiodebug.log_slow_callbacks
import ddtrace
import structlog
from ddtrace import tracer

# Logger for slow asyncio functions, like the divide() func that time.sleep(1)'s
# https://gitlab.com/quantlane/libs/aiodebug
aiodebug_logger = logging.getLogger("aiodebug.slow_tasks")

aiodebug.log_slow_callbacks.enable(
    0.05,
    on_slow_callback=lambda task_name, duration: aiodebug_logger.warning(
        "Task blocked async loop for too long",
        extra={"task_name": task_name, "duration": duration},
    ),
)

# Datadog trace information injected into logs
def tracer_injection(logger, log_method, event_dict):
    """
    Add logging event attributes into log messages that are emitted
    within functions or contexts wrapped in tracer spans (@tracer.wrap())
    """
    # get correlation ids from current tracer context
    span = tracer.current_span()
    trace_id, span_id = (span.trace_id, span.span_id) if span else (None, None)

    # add ids to structlog event dictionary
    event_dict["dd.trace_id"] = str(trace_id or 0)
    event_dict["dd.span_id"] = str(span_id or 0)

    # add the env, service, and version configured for the tracer
    event_dict["dd.env"] = ddtrace.config.env or ""
    event_dict["dd.service"] = ddtrace.config.service or ""
    event_dict["dd.version"] = ddtrace.config.version or ""

    return event_dict


# Timestamp format applied to both vanilla and structlog messages
timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

# Pre-processing for Vanilla Log messages
pre_chain = [
    # Add extra attributes of LogRecord objects to the event dictionary
    # so that values passed in the extra parameter of log methods pass
    # through to log output.
    structlog.stdlib.ExtraAdder(),
]

# Pre-processing for Structlog messages
structlog.configure(
    processors=[
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


# List of processors to be applied after pre-processing both vanilla
# and structlog messages, but before a final processor that formats
# the logs into JSON format or colored terminal output.
shared_processors = [
    # log level / logger name, effects coloring in ConsoleRenderer(colors=True)
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    # timestamp format
    timestamper,
    # To see all CallsiteParameterAdder options:
    # https://www.structlog.org/en/stable/api.html?highlight=CallsiteParameterAdder#structlog.processors.CallsiteParameterAdder
    # more options include module, pathname, process, process_name, thread, thread_name
    structlog.processors.CallsiteParameterAdder(
        {
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.LINENO,
        }
    ),
    # datadog trace id / span id / etc
    tracer_injection,
    # Any structlog.contextvars.bind_contextvars included in middleware/functions
    structlog.contextvars.merge_contextvars,
    # strip _record and _from_structlog keys from event dictionary
    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
]


def configure_logging():
    """
    Vanilla logging configs will handle messages output by structlog and
    vanilla loggers.
     - The formatter will always be ProcessorFormatter.
     - Formatters will always set foreign_pre_chain to the pre_chain
       list which pre-processes vanilla logging messages
     - structlog.configure() above handles pre-processing of structlog messages
     - To control output format use processors like ConsoleRenderer or
       JSONRenderer as extra processors on top of the shared_processors list
     - log levels can be controlled in the loggers section, handlers section,
       or external from this config with logging.getLogger(name).setLevel(level)
    """
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "color": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": shared_processors
                    + [
                        structlog.dev.ConsoleRenderer(colors=True),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": shared_processors
                    + [
                        structlog.processors.JSONRenderer(),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "color",
                    # if the below were uncommented, then this handler would
                    # filter all logs below warning, meaning no INFO or DEBUG
                    # even though we're setting the test_log.log_stuff logger
                    # to debug explicitly.
                    #
                    # "level": "WARNING",
                },
                "file": {
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": "test.log",
                    "formatter": "json",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default", "file"],
                    "level": "INFO",
                    "propagate": True,
                },
            },
        }
    )
    # Example of setting one specific logger at a level lower than loggers config
    logging.getLogger("log_test.log_stuff").setLevel(logging.DEBUG)
