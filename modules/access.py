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
IMAGES_DIR = "images"
HEATMAPS_DIR = "heatmaps"
OUT_DIR = "out"

MANIFEST_FILENAME = "manifest.json"


###############################################################################
# Exceptions                                                                          #
###############################################################################

class DuplicateJobError(Exception):
    pass


###############################################################################
# Access Tools                                                                #
###############################################################################

def save_new_data(jobid, old_data_filepath):
    print("saving new data!")
    basename = os.path.basename(old_data_filepath)

    print("basename: {}".format(basename))
    new_dir = sub_dir(jobid, DATA_DIR)

    print("new_dir: {}".format(new_dir))
    new_data_filepath = join(new_dir, basename)

    print("new_filepath: {}".format(new_data_filepath))
    shutil.copy(old_data_filepath, new_data_filepath)


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
