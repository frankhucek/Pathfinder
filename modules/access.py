'''access module

The access module encapsulates all knowledge of the project's
file structure.

In general, given the jobid of a job and the type of information
you require, the access module will return the filesystem location
of the information you are looking for.

Primary consumer: jobmanager.py

Note: the access module will look for a PATHFINDER_DIR environment
variable to set the project root directory. If such an environment
variable does not exist, it will assume the project's root directory
is this file's parent directory.
'''

###############################################################################
# Imports                                                                     #
###############################################################################

import os
from pathlib import Path
import logging

from manifest import Manifest
from chunk import create_chunks


###############################################################################
# Constants                                                                   #
###############################################################################

DEF_PATHFINDER_DIR = str(Path(__file__).parents[1])
PATHFINDER_DIR = os.environ.get("PATHFINDER_DIR",
                                DEF_PATHFINDER_DIR)

LOGS_DIR = "logs"
LOG_FILENAME = "pathfinder.log"

JOBS_DIR = "jobs"
DATA_DIR = "data"
IMAGES_DIR = "images"
HEATMAPS_DIR = "heatmaps"
SERIES_DIR = "heatmaps/series"
OUT_DIR = "out"
WEB_DIR = "web/client/src/data"

MANIFEST_FILENAME = "manifest.json"


###############################################################################
# Exceptions                                                                          #
###############################################################################

class DuplicateJobError(Exception):
    pass


###############################################################################
# Access Tools                                                                #
###############################################################################

def save_new_data(jobid, old_data_filepath, manifest):

    basename = os.path.basename(old_data_filepath)

    new_dir = sub_dir(jobid, DATA_DIR)

    filename, ext = os.path.splitext(basename)
    new_basename = filename + '.txt'
    new_data_filepath = join(new_dir, new_basename)

    # Create chunks
    chunk_width, chunk_height = manifest.chunk_dimensions()

    msg = "Calling create_chunks with dim: {}".format(chunk_width,
                                                      chunk_height)
    logger.debug(msg)
    create_chunks(old_data_filepath,
                  new_data_filepath,
                  chunk_width,
                  chunk_height)


def new_job_root():
    jobid = available_jobid()
    job_dir = job_root(jobid)
    try:
        os.mkdir(job_dir)
        return jobid
    except FileExistsError:
        raise DuplicateJobError("Duplicate job!")


def ensure_subdir(jobid, subdir):
    subdir_dir = sub_dir(jobid, subdir)
    os.makedirs(subdir_dir, exist_ok=True)


def series_heatmap_filepath(jobid, timestamp):
    series_dir = sub_dir(jobid, SERIES_DIR)
    return join(series_dir, timestamp, ".heatmap")


def series_dir(jobid):
    return sub_dir(jobid, SERIES_DIR)


def series_filepath(jobid):
    heatmap_dir = sub_dir(jobid, HEATMAPS_DIR)
    series_filename = "{}.series".format(jobid)
    return join(heatmap_dir, series_filename)


def manifest_filepath(jobid):
    root = job_root(jobid)
    return join(root, MANIFEST_FILENAME)


def out_filepath(jobid, filename):
    out_dir = sub_dir(jobid, OUT_DIR)
    return join(out_dir, filename)


def pathfinder_filepath(fp):
    return join(PATHFINDER_DIR, fp)


def manifest(jobid):
    fp = manifest_filepath(jobid)
    return Manifest.from_filepath(fp)


def heatmap_filepath(jobid):
    heatmap_dir = sub_dir(jobid, HEATMAPS_DIR)
    heatmap_filename = "{}.heatmap".format(jobid)
    return join(heatmap_dir, heatmap_filename)


def image_filepaths(jobid):
    data_dir = sub_dir(jobid, DATA_DIR)
    filenames = [f for f in os.listdir(data_dir)
                 if os.path.isfile(join(data_dir, f))]
    filepaths = [join(data_dir, f) for f in filenames]
    return filepaths


def out_dir_filepath(jobid):
    return sub_dir(jobid, OUT_DIR)


def web_filepath(jobid):
    return pathfinder_filepath(WEB_DIR)


def web_data_images_filepath(jobid):
    return join(web_filepath(jobid), "images")


def web_data_out_filepath(jobid):
    return join(web_filepath(jobid), "out")


def log_filepath():
    log_dir = pathfinder_filepath(LOGS_DIR)
    return join(log_dir, LOG_FILENAME)


###############################################################################
# Helpers                                                                     #
###############################################################################

def join(*args, **kwargs):
    return os.path.join(*args)


def jobs_dir():
    return join(PATHFINDER_DIR, JOBS_DIR)


def job_root(jobid):
    return join(jobs_dir(), str(jobid))


def sub_dir(jobid, subdir):
    root = job_root(jobid)
    return join(root, subdir)


def available_jobid():

    _, job_dirs, _ = next(os.walk(jobs_dir()))
    jobids = sorted([int(x) for x in job_dirs])

    for idx, existing_jobid in enumerate(jobids):
        if existing_jobid != idx:
            return idx

    next_jobid = len(jobids)
    return next_jobid


###############################################################################
# Logging                                                                     #
###############################################################################

logger = logging.getLogger(__name__)
