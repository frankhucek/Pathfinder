

###############################################################################
# Imports                                                                     #
###############################################################################

import os
import logging
import access
import image


###############################################################################
# Constants                                                                   #
###############################################################################

level_str = os.environ.get("PATHFINDER_LOG_LEVEL", "DEBUG")
LEVEL = getattr(logging, level_str)

FORMAT = "%(levelname)s:%(asctime)s:%(message)s"


###############################################################################
# Log tools                                                                   #
###############################################################################

def start_log():
    log_path = access.log_filepath()
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(filename=log_path,
                        level=LEVEL,
                        format=FORMAT,
                        datefmt=image.DATETIME_FMT)


###############################################################################
# Helper functions                                                            #
###############################################################################
