#! /usr/bin/env python3

'''Job manager module

The job manager module is responsible for handling incoming data
for a job. It handles any incremental processing that must be done
to keep a job up to date once it receives new data.

This keeps lots of processing information isolated from the server
code.

The job manager uses the Processing class/subclasses to determine
what behavior to follow for each job when it receives new data.
The job manifest will specificy a processing_type that corresponds
to a Processing subclass. Then, that subclass will implement the
Processing.process(jobid, filename) method, which is called on
the incoming data.

The jobmanager can be called programmatically with the update_job
function. It also provides a CLI in this file.
'''


###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import shutil
from datetime import timedelta

# star import required for unpickling
# need to have all heatmap helper classes imported to
# __main__ in this script in order for unpickling to work
# TODO: work around this by refactoring
from heatmap import *
from image import ImageData
import heatmap
import access


###############################################################################
# Constants                                                                   #
###############################################################################

NEW_JOB_DIRS = [
    access.DATA_DIR,
    access.IMAGES_DIR,
    access.HEATMAPS_DIR,
    access.OUT_DIR
]


###############################################################################
# Classes                                                                     #
###############################################################################

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]


class Processing(object):

    @classmethod
    def _types(cls):
        return {x.processing_type: x
                for x in all_subclasses(cls)}

    @staticmethod
    def of(manifest, processing_json):
        processing_type = manifest.processing_type(processing_json)
        types = Processing._types()
        subclass = types.get(processing_type, None)
        if subclass:
            return subclass(manifest, processing_json)
        else:
            msg = "Unrecognized processing type: {}".format(processing_type)
            raise ValueError(msg)

    @staticmethod
    def all_from(manifest, jobid):
        instructions = manifest.processing()
        for instruction in instructions:
            yield Processing.of(manifest, instruction)

    @classmethod
    def setup_all(cls, manifest, jobid):
        for processing in cls.all_from(manifest, jobid):
            processing.setup(jobid)
        # map(cls.setup, cls.all_from(manifest, jobid))

    def __init__(self, manifest, json):
        super().__init__()
        self.manifest = manifest
        self.json = json

    def setup(self, jobid):
        print("setting up {}".format(self.processing_type))

    def process(self, jobid, filename):
        raise NotImplementedError("implement in subclass")


class ProcessEveryImage(Processing):

    processing_type = "update_on_every_image"

    WINDOW_SIZE = "window_size"
    COLOR_THRESH = "color_thresh"
    TIME_WINDOW = "time_window"

    def __init__(self, manifest, json):
        super().__init__(manifest, json)
        self.window_size = json[ProcessEveryImage.WINDOW_SIZE]
        self.color_thresh = json[ProcessEveryImage.COLOR_THRESH]
        self.time_window = json[ProcessEveryImage.TIME_WINDOW]

    def _delta(self):
        return timedelta(seconds=self.time_window)

    def _period(self, filename):
        img_data = ImageData.create(self.manifest, filename)
        end_time = img_data.time_taken()
        start_time = end_time - self._delta()
        return heatmap.TimePeriod(start_time, end_time)

    def setup(self, jobid):
        super().setup(jobid)
        gen_heatmap(jobid)

    def process(self, jobid, filename):
        heatmap_filepath = access.heatmap_filepath(jobid)
        period = self._period(filename)
        img_files = access.image_filepaths(jobid)
        heatmap.record_heatmap(heatmap_filepath,
                               img_files,
                               period,
                               self.window_size,
                               self.color_thresh)


class IntervalProcessing(Processing):

    processing_type = "interval_processing"

    WINDOW_SIZE = "window_size"
    COLOR_THRESH = "color_thresh"
    INTERVAL = "interval"

    def __init__(self, manifest, json):
        super().__init__(manifest, json)
        self.window_size = json[IntervalProcessing.WINDOW_SIZE]
        self.color_thresh = json[IntervalProcessing.COLOR_THRESH]
        interval_sec = json[IntervalProcessing.INTERVAL]
        self.interval = timedelta(seconds=interval_sec)

    def _period(self, hm, img_data):
        print("last update: {}".format(hm.last_update()))
        return heatmap.TimePeriod(hm.last_update(),
                                  img_data.time_taken())

    def _should_update(self, hm, img_data):
        period = self._period(hm, img_data)
        return period.duration() > self.interval

    def setup(self, jobid):
        super().setup(jobid)
        gen_heatmap(jobid)

    def process(self, jobid, filename, heatmap_filepath=None):
        if not heatmap_filepath:
            heatmap_filepath = access.heatmap_filepath(jobid)
        hm = Heatmap.load(heatmap_filepath)
        img_data = ImageData.create(self.manifest, filename)

        if self._should_update(hm, img_data):
            print("Updating for img: {}".format(img_data.time_taken()))
            period = self._period(hm, img_data)
            img_files = access.image_filepaths(jobid)
            heatmap.record_heatmap(heatmap_filepath,
                                   img_files,
                                   period,
                                   self.window_size,
                                   self.color_thresh)
        else:
            print("Not updating for img: {}".format(img_data.time_taken()))


class AllResultsProcessing(Processing):

    processing_type = "all_results_processing"

    def setup(self, jobid):
        super().setup(jobid)

    def process(self, jobid, filename):

        heatmap_filepath = access.heatmap_filepath(jobid)

        view_heatmap_fp = access.out_filepath(jobid, "heatmap.bmp")
        heatmap.view_heatmap(heatmap_filepath,
                             view_heatmap_fp)

        overlay_fp = access.out_filepath(jobid, "overlay.bmp")
        control_fp = access.pathfinder_filepath(self.manifest.control_img())
        heatmap.overlay_heatmap(heatmap_filepath,
                                control_fp,
                                overlay_fp,
                                self.manifest.scale(),
                                self.manifest.blur())


class SeriesProcessing(Processing):

    processing_type = "series_processing"

    SERIES_INTERVAL = "series_interval"
    SERIES_START = "series_start"

    def __init__(self, manifest, json):
        super().__init__(manifest, json)
        series_interval_sec = json[SeriesProcessing.SERIES_INTERVAL]
        self.series_interval = timedelta(seconds=series_interval_sec)
        series_start_str = json[SeriesProcessing.SERIES_START]
        self.series_start = image.parse_datetime(series_start_str)

    def setup(self, jobid):
        super().setup(jobid)

        # make sure series subdir will exist (heatmaps/series)
        access.ensure_subdir(jobid, access.SERIES_DIR)

        # generate blank series object
        series_filepath = access.series_filepath(jobid)
        manifest = access.manifest(jobid)
        interval = self.series_interval
        start = self.series_start
        heatmap.new_series_heatmap(series_filepath,
                                   manifest,
                                   interval,
                                   start)

    def process(self, jobid, filename):

        series_filepath = access.series_filepath(jobid)
        series_dir = access.series_dir(jobid)
        subheatmap_fp = heatmap.series_subheatmap(series_filepath,
                                                  filename,
                                                  series_dir)
        interval_proc = IntervalProcessing(self.manifest, self.json)
        interval_proc.process(jobid, filename, subheatmap_fp)


###############################################################################
# Utilities                                                                   #
###############################################################################

def update_job(jobid, incoming_data_filepath):
    manifest = access.manifest(jobid)
    access.save_new_data(jobid, incoming_data_filepath, manifest)
    instructions = manifest.processing()

    # execute each of the processing instructions found in job's manifest
    for instruction in instructions:
        processing = Processing.of(manifest, instruction)
        processing.process(jobid, incoming_data_filepath)


def new_job(incoming_manifest):

    # create job dir
    jobid = access.new_job_root()

    # ensure all required subdirs exist
    for subdir in NEW_JOB_DIRS:
        access.ensure_subdir(jobid, subdir)

    # copy in manifest
    manifest_filepath = access.manifest_filepath(jobid)
    shutil.copy(incoming_manifest, manifest_filepath)

    # do setup for each processing type
    manifest = access.manifest(jobid)
    Processing.setup_all(manifest, jobid)

    # report new jobid
    return jobid


###############################################################################
# Helper functions                                                            #
###############################################################################

def gen_heatmap(jobid):
    heatmap_filepath = access.heatmap_filepath(jobid)
    manifest = access.manifest(jobid)
    heatmap.new_heatmap(heatmap_filepath, manifest)


def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="op")

    update_job = subparsers.add_parser("update_job")

    update_job.add_argument("jobid",
                            type=int,
                            help="id of job")
    update_job.add_argument("data_filepath",
                            help="location of incoming data")

    new_job = subparsers.add_parser("new_job",
                                    help="add a new job")

    new_job.add_argument("manifest_filepath",
                         help="file containing a manifest")

    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():

    args = get_args()

    if args.op == "update_job":
        update_job(args.jobid,
                   args.data_filepath)

    elif args.op == "new_job":
        jobid = new_job(args.manifest_filepath)
        print("Created new job: {}".format(jobid))


if __name__ == '__main__':
    main()
