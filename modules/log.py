

###############################################################################
# Imports                                                                     #
###############################################################################

import os
import sys
import logging
import access
import image


###############################################################################
# Constants                                                                   #
###############################################################################

FORMAT = "\
%(levelname)s \
%(module)s/%(funcName)s(%(asctime)s): \
%(message)s"

LOG_LEVEL_ENV = "PATHFINDER_LOG_LEVEL"

DEFAULT_FILE_LEVEL = logging.INFO
DEFAULT_STDERR_LEVEL = logging.WARNING


###############################################################################
# Formatters                                                                  #
###############################################################################

formatter = logging.Formatter(fmt=FORMAT,
                              datefmt=image.DATETIME_FMT)


###############################################################################
# Log tools                                                                   #
###############################################################################

def start_log():
    log_path = init_log_file()
    level = log_level()

    file_handler = make_file_handler(level, log_path)
    stream_handler = make_stream_handler()

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    root_logger.info("starting log")


###############################################################################
# Helper functions                                                            #
###############################################################################

def make_file_handler(level, log_path):
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    return file_handler


def make_stream_handler():
    stream_handler = logging.StreamHandler(stream=sys.stderr)
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    return stream_handler


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
