#! /usr/bin/env python3

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import datetime

# star import required for unpickling
# need to have all heatmap helper classes imported to
# __main__ in this script in order for unpickling to work
# TODO: work around this by refactoring
from heatmap import *
import heatmap
import access


###############################################################################
# Classes                                                                     #
###############################################################################

class Processing(object):

    @classmethod
    def _types(cls):
        return {x.processing_type: x
                for x in cls.__subclasses__()}

    @staticmethod
    def of(manifest):
        json = manifest.processing()
        processing_type = manifest.processing_type()
        types = Processing._types()
        subclass = types.get(processing_type, None)
        if subclass:
            return subclass(manifest, json)
        else:
            raise ValueError("Unrecognized processing type")

    def __init__(self, manifest, json):
        super().__init__()
        self.manifest = manifest
        self.json = json

    def process(self, filename):
        raise NotImplementedError("implement is subclass")


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
        return datetime.timedelta(seconds=self.time_window)

    def _period(self, filename):
        img_data = ImageData.create(self.manifest, filename)
        end_time = img_data.time_taken()
        start_time = end_time - self._delta()
        return heatmap.TimePeriod(start_time, end_time)

    def process(self, jobid, filename):
        heatmap_filepath = access.heatmap_filepath(jobid)
        period = self._period(filename)
        img_files = access.image_filepaths(jobid)
        heatmap.record_heatmap(heatmap_filepath,
                               img_files,
                               period,
                               self.window_size,
                               self.color_thresh)


###############################################################################
# Utilities                                                                          #
###############################################################################

def update_job(jobid, incoming_data_filepath):
    access.save_new_data(jobid, incoming_data_filepath)
    manifest = access.manifest(jobid)
    processing = Processing.of(manifest)
    processing.process(jobid, incoming_data_filepath)


###############################################################################
# Helper functions                                                            #
###############################################################################

def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="op")

    update_job = subparsers.add_parser("update_job")

    update_job.add_argument("jobid",
                            type=int,
                            help="id of job")
    update_job.add_argument("data_filepath",
                            help="location of incoming data")

    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():

    args = get_args()

    if args.op == "update_job":
        update_job(args.jobid,
                   args.data_filepath)


if __name__ == '__main__':
    main()
