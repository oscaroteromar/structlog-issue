import structlog
from structlog.types import BindableLogger, EventDict, Processor


class DummyProcessor:
    """Dummy class to see if `logger` is None.

    See the commented lines below to see how the real case is.
    We would like to check the log level of the logger to run
    some code. Since the `logger` is None, we never access to the
    second part of the condition.
    """

    def __call__(self, logger: BindableLogger | None, method_name: str, event_dict: EventDict) -> dict:
        # The real behaviour would be something like:
        # if logger is not None and not logger.isEnabledFor(logging.DEBUG):
        # print("Run some code")
        print(f"logger argument is {logger}")
        return event_dict


COMMON_PROCESSORS: list[Processor] = [
    # Add structlog context variables to log lines (includes thread locals)
    structlog.contextvars.merge_contextvars,
    # Dummy
    DummyProcessor(),
    # Add the name of the logger to the record
    structlog.stdlib.add_logger_name,
    # Adds the log level as a parameter of the log line
    structlog.stdlib.add_log_level,
    # Adds a timestamp for every log line
    structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S%z"),
    # If the log record contains a string in byte format, this will
    # automatically convert it into a utf-8 string
    structlog.processors.UnicodeDecoder(),
    # Unpack exception info in log entry
    structlog.processors.format_exc_info,
    # Perform old school %-style formatting. on the log msg/event
    structlog.stdlib.PositionalArgumentsFormatter(),
]


def logging_config(
    log_level: str = "INFO",
    processors: list[Processor] = [],
    remove_metadata: bool = True,
) -> dict:
    """Setup logging configuration with structlog features.

    This function configures processors and formatters to use with the standard
    logging module from Python, using structlog features.

    Args:
        log_level: The level at which to configure the loggers.
        processors: A list of event processors to apply to each log entry.
        remove_metadata: Parameter implemented mainly for debugging purposes.
            It allows to switch on or off the addition of the log entry
            procedence to the output.
    """
    logging_processors: list[Processor] = [
        # Add extra attributes of LogRecord objects to the event dictionary
        # so that values passed in the extra parameter of log methods pass
        # through to log output.
        structlog.stdlib.ExtraAdder(),
    ]

    meta_remover: list[Processor] = []
    if remove_metadata:
        # Remove `_record` and `_from_structlog` keys from log event
        meta_remover.append(structlog.stdlib.ProcessorFormatter.remove_processors_meta)

    # Configure logging (with structlog format)
    logging_config: dict = {
        "version": 1,
        # allow any third party logging output to be set up by this
        # configuration
        "disable_existing_loggers": False,
        "formatters": {
            "pretty": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    *meta_remover,
                    # Render event in colored key-value format.
                    structlog.dev.ConsoleRenderer(colors=True),
                ],
                "foreign_pre_chain": [
                    *logging_processors,
                    *processors,
                ],
            },
        },
        "handlers": {"base": {"class": "logging.StreamHandler", "level": log_level, "formatter": "pretty"}},
        "loggers": {
            "": {
                "handlers": ["base"],
                "level": log_level,
                "propagate": False,
            }
        },
    }

    return logging_config


def structlog_config(processors: list[Processor] = [], cache: bool = True) -> dict:
    """Provide a default configuration for structlog.

    Args:
        processors: A list of event processors to apply to structlog entries
            only.
        cache: A bool to signal the save of the logger configuration on first
            use. May be useful to enforce isolation during testing.
    """

    return {
        "processors": [
            # Filter log entries by level
            structlog.stdlib.filter_by_level,
            *processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # Used to create wrapped loggers that are used for OUTPUT.
        "logger_factory": structlog.stdlib.LoggerFactory(),
        # The bound logger that you get back from get_logger().
        # This one imitates the API of `logging.Logger`.
        "wrapper_class": structlog.stdlib.BoundLogger,
        # Effectively freeze configuration after creating the first bound logger.
        "cache_logger_on_first_use": cache,
    }


def configure_logging(loglevel: str) -> dict:
    """Generates logging configuration for `logging` and `structlog`.

    Args:
        loglevel: String in upper case indicating the log level.
        logfile: File to log in.
        logdir: Directory where logfile resides.

    Returns:
        `logging` configuration in dictionary format.
    """
    processors: list[Processor] = COMMON_PROCESSORS[:]
    logging_conf = logging_config(log_level=loglevel, processors=processors)
    structlog.configure(**structlog_config(processors=processors))

    return logging_conf
