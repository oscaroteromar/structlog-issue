"""
Problem to be solved:
When using structlog logger, the `logger` argument that arrives to
`DummyProcessor` (in logging_config.py file), is a not null object.
However, when logging when Python's logging library, the given argument
is None.

Current output:
$ python main.py
logger argument is <_FixedFindCallerLogger testing_sructlog (DEBUG)>
2024-04-05T15:02:51+0000 [debug    ] A log test from logging.       [testing_sructlog]
logger argument is None
2024-04-05T15:02:51+0000 [debug    ] A log test from structlog.     [testing_sructlog]

Expected output (more or less):
$ python main.py
logger argument is <_FixedFindCallerLogger testing_sructlog (DEBUG)>
2024-04-05T15:02:51+0000 [debug    ] A log test from logging.       [testing_sructlog]
logger argument is <a valid object like logging.Logger> 
2024-04-05T15:02:51+0000 [debug    ] A log test from structlog.     [testing_sructlog]

"""

import logging
import logging.config

import structlog

from logging_config import configure_logging

logging.config.dictConfig(configure_logging("DEBUG"))


def test_structlog():
    logger = structlog.stdlib.get_logger("testing_sructlog")
    logger.debug("A log test from logging.")


def test_logging():
    logger = logging.getLogger("testing_sructlog")
    logger.debug("A log test from structlog.")


if __name__ == "__main__":
    for m in (test_structlog, test_logging):
        m()
