

###############################################################################
# Imports                                                                     #
###############################################################################

import os
import shutil
from pathlib import Path

from manifest import Manifest


###############################################################################
# Constants                                                                   #
###############################################################################

DEF_PATHFINDER_DIR = str(Path(__file__).parents[1])
PATHFINDER_DIR = os.environ.get("PATHFINDER_DIR",
                                DEF_PATHFINDER_DIR)
JOBS_DIR = "jobs"
DATA_DIR = "data"
HEATMAPS_DIR = "heatmaps"

MANIFEST_FILENAME = "manifest.json"


###############################################################################
# Access Tools                                                                #
###############################################################################

def save_new_data(jobid, old_data_filepath):
    basename = os.path.basename(old_data_filepath)

    new_dir = sub_dir(jobid, DATA_DIR)
    new_data_filepath = join(new_dir, basename)

    shutil.move(old_data_filepath, new_data_filepath)


def manifest_filepath(jobid):
    root = job_root(jobid)
    return join(root, MANIFEST_FILENAME)


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