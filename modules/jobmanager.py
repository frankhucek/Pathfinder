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
import logging
from datetime import timedelta

# star import required for unpickling
# need to have all heatmap helper classes imported to
# __main__ in this script in order for unpickling to work
# TODO: work around this by refactoring
from heatmap import *
from image import ImageData
import heatmap
import access
import crowd
import retail
import log


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

    @classmethod
    def process_all(cls, manifest, jobid, filename):
        for processing in cls.all_from(manifest, jobid):
            proc_type = processing.processing_type
            msg = "Processing job {}: {}".format(jobid, proc_type)
            logger.info(msg)

            processing.process(jobid, filename)

    def __init__(self, manifest, json):
        super().__init__()
        self.manifest = manifest
        self.json = json

    def setup(self, jobid):
        logger.info("Setting up {}".format(self.processing_type))

    def process(self, jobid, filename):
        pass


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

    def setup(self, jobid):
        super().setup(jobid)
        gen_heatmap(jobid)

    def process(self, jobid, filename, heatmap_filepath=None):
        if not heatmap_filepath:
            heatmap_filepath = access.heatmap_filepath(jobid)

        interval = UpdateIntervalChecker(self.manifest,
                                         self.json,
                                         filename,
                                         heatmap_filepath)

        if interval.should_update():
            msg = "Updating for img: {}".format(interval.time_taken())
            logger.debug(msg)
            img_files = access.image_filepaths(jobid)
            heatmap.record_heatmap(heatmap_filepath,
                                   img_files,
                                   interval.period(),
                                   self.window_size,
                                   self.color_thresh)
        else:
            msg = "Not updating for img: {}".format(interval.time_taken())
            logger.debug(msg)


class AllResultsProcessing(Processing):

    processing_type = "all_results_processing"

    def process(self, jobid, filename):

        heatmap_filepath = access.heatmap_filepath(jobid)

        view_heatmap_fp = access.out_filepath(jobid, "heatmap.bmp")
        heatmap.view_heatmap(heatmap_filepath,
                             view_heatmap_fp)

        overlay_fp = access.out_filepath(jobid, "overlay.bmp")
        control_fp = access.specific_image(jobid, self.manifest.control_img())
        heatmap.overlay_heatmap(heatmap_filepath,
                                control_fp,
                                overlay_fp,
                                self.manifest.scale(),
                                self.manifest.blur())


class ProjectProcessing(Processing):

    processing_type = "project_processing"

    PROJECT_WIDTH = "project_width"

    def __init__(self, manifest, json):
        super().__init__(manifest, json)
        self.project_width = json[ProjectProcessing.PROJECT_WIDTH]

    def process(self, jobid, filename):

        heatmap_filepath = access.heatmap_filepath(jobid)
        interval = ProjectIntervalChecker(self.manifest,
                                          self.json,
                                          filename,
                                          heatmap_filepath)

        if interval.should_update():
            project_fp = access.out_filepath(jobid, "project.bmp")
            heatmap.project_heatmap(heatmap_filepath,
                                    project_fp,
                                    self.project_width,
                                    interval.time_taken())


class CrowdProcessing(Processing):

    processing_type = "crowd_processing"

    UNITS = "units"
    AGGREGATE = "aggregate"

    def __init__(self, manifest, json):
        super().__init__(manifest, json)
        units_string = json[CrowdProcessing.UNITS]
        self.units = crowd.FrequencyUnits.of(units_string)
        self.aggregate = json[CrowdProcessing.AGGREGATE]

    def process(self, jobid, filename):

        heatmap_filepath = access.heatmap_filepath(jobid)

        crowd_total_fp = access.out_filepath(jobid, "total.json")
        crowd.write_total(heatmap_filepath,
                          crowd_total_fp)

        series_filepath = access.series_filepath(jobid)
        crowd_frequencies_fp = access.out_filepath(jobid, "frequencies.json")
        crowd.write_frequency(series_filepath,
                              crowd_frequencies_fp,
                              self.units,
                              self.aggregate)


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


class OutputCopyProcessing(Processing):

    processing_type = "output_copy_processing"

    def setup(self, jobid):
        super().setup(jobid)

        # make sure top level data directory exists
        os.makedirs(access.web_filepath(jobid), exist_ok=True)

        # make sure images directory exists
        os.makedirs(access.web_data_images_filepath(jobid), exist_ok=True)

    def process(self, jobid, filename):
        basename = os.path.basename(filename)
        web_filepath = access.web_data_images_filepath(jobid)
        new_data_filepath = os.path.join(web_filepath, basename)

        shutil.copy(filename, new_data_filepath)
        self.process_out_dir(jobid, filename)

    def process_out_dir(self, jobid, filepath):
        web_out_filepath = access.web_data_out_filepath(jobid)
        out_filepath = access.out_dir_filepath(jobid)
        force_copy(out_filepath, web_out_filepath)


class RetailProcessing(Processing):

    processing_type = "retail_processing"

    HOTDOG_LIMIT = "hotdog_limit"

    def __init__(self, manifest, json):
        super().__init__(manifest, json)
        self.hotdog_limit = json[RetailProcessing.HOTDOG_LIMIT]

    def process(self, jobid, filename):
        heatmap_filepath = access.heatmap_filepath(jobid)
        control_image = access.specific_image(jobid, 0)
        retail_json = access.out_filepath(jobid, "retail.json")
        retail_jpeg = access.out_filepath(jobid, "retail.jpeg")
        retail.create_retail(heatmap_filepath, retail_json, self.hotdog_limit)
        retail.create_retail_img(control_image, retail_json, retail_jpeg)


class IntervalChecker(object):

    INTERVAL = "interval"

    def __init__(self, manifest, json, img_fp, heatmap_fp):
        super().__init__()
        self.manifest = manifest
        self.json = json

        interval_sec = json[self.INTERVAL]
        self.interval = timedelta(seconds=interval_sec)

        self.img = ImageData.create(manifest, img_fp)
        self.hm = Heatmap.load(heatmap_fp)

    def prev_time(self):
        raise NotImplementedError("implement")

    def period(self):
        return heatmap.TimePeriod(self.prev_time(),
                                  self.img.time_taken())

    def should_update(self):
        period = self.period()
        return period.duration() > self.interval

    def time_taken(self):
        return self.img.time_taken()


class UpdateIntervalChecker(IntervalChecker):

    def prev_time(self):
        return self.hm.last_update()


class ProjectIntervalChecker(IntervalChecker):

    def prev_time(self):
        return self.hm.last_project()


###############################################################################
# Utilities                                                                   #
###############################################################################

def update_job(jobid, incoming_data_filepath):

    logger.info("Updating job {} with {}"
                .format(jobid, incoming_data_filepath))

    manifest = access.manifest(jobid)

    access.save_new_data(jobid, incoming_data_filepath, manifest)

    Processing.process_all(manifest, jobid, incoming_data_filepath)


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

    logger.info("Created new job: {}".format(jobid))

    # report new jobid
    return jobid


###############################################################################
# Logging                                                                     #
###############################################################################

logger = logging.getLogger(__name__)


###############################################################################
# Helper functions                                                            #
###############################################################################

def force_copy(src, dest):
    if (os.path.exists(dest)):
            shutil.rmtree(dest)
    shutil.copytree(src, dest)


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

    log.start_log()

    args = get_args()

    if args.op == "update_job":
        update_job(args.jobid,
                   args.data_filepath)

    elif args.op == "new_job":
        jobid = new_job(args.manifest_filepath)
        print("Created new job: {}".format(jobid))


if __name__ == '__main__':
    main()
