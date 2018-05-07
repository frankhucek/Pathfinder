

###############################################################################
# Imports                                                                     #
###############################################################################

import os
import sys
import logging
import logging.handlers
import access
import image


###############################################################################
# Constants                                                                   #
###############################################################################

FORMAT = "\
{levelname} \
{module}:{lineno}/{funcName}({asctime}): \
{message}"

SYSLOG_FORMAT = "\
[pathfinder]: {}"\
.format(FORMAT)

LOG_LEVEL_ENV = "PATHFINDER_LOG_LEVEL"

DEFAULT_FILE_LEVEL = logging.INFO
DEFAULT_STDERR_LEVEL = logging.WARNING
DEFAULT_SYSLOG_LEVEL = logging.ERROR

BYTES_PER_MEGABYTE = 1024 * 1024
LOG_SIZE = 10 * BYTES_PER_MEGABYTE
BACKUP_COUNT = 10


###############################################################################
# Formatters                                                                  #
###############################################################################

formatter = logging.Formatter(fmt=FORMAT,
                              datefmt=image.DATETIME_FMT,
                              style="{")

syslog_formatter = logging.Formatter(fmt=SYSLOG_FORMAT,
                                     datefmt=image.DATETIME_FMT,
                                     style="{")


###############################################################################
# Log tools                                                                   #
###############################################################################

def start_log():
    log_path = init_log_file()
    level = log_level()

    file_handler = make_file_handler(level, log_path)
    stream_handler = make_stream_handler()
    syslog_handler = make_syslog_handler()

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(syslog_handler)

    root_logger.info("starting log")


###############################################################################
# Helper functions                                                            #
###############################################################################

def make_file_handler(level, log_path):
    file_handler = \
        logging.handlers\
        .RotatingFileHandler(log_path,
                             maxBytes=LOG_SIZE,
                             backupCount=BACKUP_COUNT)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    return file_handler


def make_stream_handler():
    stream_handler = logging.StreamHandler(stream=sys.stderr)
    stream_handler.setLevel(DEFAULT_STDERR_LEVEL)
    stream_handler.setFormatter(formatter)
    return stream_handler


def make_syslog_handler():
    syslog_handler = \
        logging.handlers.SysLogHandler(address='/dev/log')
    syslog_handler.setLevel(DEFAULT_SYSLOG_LEVEL)
    syslog_handler.setFormatter(syslog_formatter)
    return syslog_handler


def init_log_file():
    log_path = access.log_filepath()
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    return log_path


def log_level():
    level_str = os.environ.get(LOG_LEVEL_ENV, None)
    if level_str:
        level = getattr(logging, level_str)
    else:
        level = DEFAULT_FILE_LEVEL
    return level
