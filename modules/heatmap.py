#! /usr/bin/env python3

'''Pathfinder heatmap module

This module holds all tools used for manipulating heatmaps.

The heatmap module is independent from the project file structure.
That is, all inputs and outputs to heatmap.py are in the form of
filepaths.

heatmap.py provides an API in the Heatmap Tools section of this file.
These functions are programmatic ways to perform operations such as
generating a new heatmap object, recording images onto a heatmap,
projecting the heatmap into the blueprint space described by a
certain manifest, and so on. Examples:
new_heatmap(...)
record_heatmap(...)
view_heatmap(...)
project_heatmap(...)
overlay_heatmap(...)

The heatmap API can also be access by the command line interface
defined in this file.

The module makes use of a Python Heatmap object for most of these
operations. The Heatmap object can be saved and loaded as a binary
file using pickle. Users of the heatmap API should consider the
Heatmap object to be an implementation detail.

Further descriptions of the heatmapping algorithms used can be
found in the Pathfinder design document.
'''


###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import json
import pickle
import os
import logging

from datetime import datetime, timedelta

import numpy as np
from PIL import Image
from PIL import ImageFilter
from PIL import ImageOps

from manifest import Manifest
from mapping import Geometry
import mapping
import cli
import image
import log


###############################################################################
# Constants                                                                   #
###############################################################################

DEFAULT_WINDOW_SIZE = 2
DEFAULT_COLOR_THRESH = 50

PROJECT_BG = (105, 180, 234)
PROJECT_FG = (255, 193, 119)


###############################################################################
# Classes                                                                     #
###############################################################################

class TimePeriod(object):

    def __init__(self, start, end):
        super(TimePeriod, self).__init__()
        self.start = start
        self.end = end

    def contains(self, dt):
        return self.start <= dt and dt <= self.end

    def expand_to_include(self, dt):
        if dt < self.start:
            return TimePeriod(dt, self.end)
        elif dt > self.end:
            return TimePeriod(self.start, dt)
        else:
            return self

    @staticmethod
    def union(tp1, tp2):
        if not tp1:
            return tp2
        elif not tp2:
            return tp1
        return TimePeriod(min(tp1.start, tp2.start),
                          max(tp1.end, tp2.end))

    def duration(self):
        return self.end - self.start

    def __str__(self):
        return "[{}, {}]".format(self.start, self.end)


class NullTimePeriod(object):

    def __init__(self):
        self.start = datetime(1, 1, 1, 0, 0, 0)
        self.end = datetime(1, 1, 1, 0, 0, 0)

    def contains(self, dt):
        return False

    def expand_to_include(self, dt):
        return TimePeriod(dt, dt)

    def duration(self):
        return timedelta(seconds=0)


class CoordRange(object):

    def __init__(self, image_corners):
        self._min_x = min(x for x, y in image_corners)
        self._max_x = max(x for x, y in image_corners)
        self._min_y = min(y for x, y in image_corners)
        self._max_y = max(y for x, y in image_corners)

    def contains(self, coord):
        x, y = coord
        return self._min_x <= x and x <= self._max_x and \
            self._min_y <= y and y <= self._max_y

    def coordinates(self):
        for x in range(self._min_x, self._max_x + 1):
            for y in range(self._min_y, self._max_y + 1):
                yield (x, y)


class Heatmap(object):

    @staticmethod
    def new(manifest):
        width, height = manifest.dimensions()
        points = np.zeros((height, width))
        return Heatmap(manifest, points)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def __init__(self, manifest, points):
        super(Heatmap, self).__init__()
        self.manifest = manifest
        self.size = manifest.dimensions()
        self.geom = Geometry.from_manifest(manifest)
        self.field = CoordRange(manifest.image_corners())
        self.count = 0
        self._points = points
        self._rgb = np.zeros((points.shape[0], points.shape[1], 3))
        self.period = NullTimePeriod()
        self.project_period = NullTimePeriod()

    def add(self, coord):
        self.count += 1
        self.set(coord, self.at(coord) + 1)

    def set(self, coord, val):
        x, y = coord
        self._points[y, x] = val
        self._rgb[y, x, 0] = val

    def at(self, coord):
        return self._points[self._flip(coord)]

    def _flip(self, coord):
        x, y = coord
        return y, x

    def record(self,
               img_files,
               period,
               window_size=DEFAULT_WINDOW_SIZE,
               color_thresh=DEFAULT_COLOR_THRESH):
        data_type = image.ImageData.sub_type(img_files)

        images = image_obj_sequence(self.manifest,
                                    img_files,
                                    period)

        image_sets = windows(images, window_size)

        for idx, image_set in enumerate(image_sets):

            all_coordinates = data_type.coordinates(self.manifest,
                                                    self.size)
            for coord in all_coordinates:

                self.include_in_period(image_set)
                if is_movement(image_set, coord, color_thresh):
                    image_set[0].register(self, coord)

    def include_in_period(self, image_set):
        first_dt = image_set[0].time_taken()
        last_dt = image_set[-1].time_taken()
        self.period = self.period.expand_to_include(first_dt)
        self.period = self.period.expand_to_include(last_dt)

    def last_update(self):
        return self.period.end

    def last_project(self):
        return self.project_period.end

    def points(self):
        m = np.max(self._points)
        if m == 0:
            return self._points
        else:
            return self._points / m

    def project_point(self, coord, scale):
        logger.debug("projecting coord {} at size {}".format(coord, self.size))
        raw = mapping.image_to_blueprint(coord,
                                         self.geom,
                                         self.size)

        projected = tuple(int(round(x * scale)) for x in raw)
        return projected

    def project(self, filepath, desired_width, moment=None):

        self.project_period = \
            self.project_period\
                .expand_to_include(moment)

        logger.debug("Project: filepath = {}".format(filepath))

        image_corners = self.manifest.image_corners()
        lower_right = image_corners[3]
        b_x, b_y = self.project_point(lower_right, 1)

        scale = desired_width / b_x
        new_size = (int(b_y * scale), int(b_x * scale))
        blueprint_values = np.zeros(new_size)

        logger.debug("Project: new size = {}".format)

        def valid_coord(coord, shape):
            return all(c >= 0 and c < s
                       for c, s in zip(coord, shape))

        for x, y in self.field.coordinates():

            val = self.at((x, y))

            p_x, p_y = self.project_point((x, y), scale)

            if valid_coord((p_y, p_x), blueprint_values.shape):
                blueprint_values[p_y, p_x] += val

        maximum = np.max(blueprint_values)
        div = maximum if maximum else 1
        normalized = blueprint_values / div
        self.write_project_binary(normalized, filepath)

    def overlay(self, img, filepath, scale, blur):

        maximum = np.max(self._rgb)
        div = maximum if maximum else 1
        points = self._rgb / div

        # scale redshift by specified degree
        scaled_points = points * scale

        # convert to Image for blurring
        red_points_8bit = scaled_points.astype('uint8')
        red_img = Image.fromarray(red_points_8bit)
        filtered_red_img = red_img.filter(ImageFilter.GaussianBlur(blur))

        # convert backto float64 numpy arrays
        # numpy arrays: so we can add
        # float64: to avoid 8bit overflow
        red_points = np.asarray(filtered_red_img, dtype='float64')
        img_points = np.asarray(img, dtype='float64')

        combined_points = img_points + red_points

        # must clip red values outside of range
        # these might occur because of the redshifting
        clipped_points = np.clip(combined_points, 0, 255)
        clipped_points_8bit = clipped_points.astype('uint8')

        overlaid = Image.fromarray(clipped_points_8bit)
        overlaid.save(filepath)

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    def write(self, filepath):
        self.write_bw_binary(self.points(), filepath)

    @staticmethod
    def write_bw_binary(arr, filepath):
        write_points = arr * 255
        uint_points = write_points.astype('uint8')
        im = Image.fromarray(uint_points, 'L')
        im.save(filepath)

    @staticmethod
    def write_project_binary(arr, filepath):
        write_points = arr * 255
        uint_points = write_points.astype('uint8')
        im = Image.fromarray(uint_points, 'L')
        rgb_im = ImageOps.colorize(im,
                                   PROJECT_BG,
                                   PROJECT_FG)
        rgb_im.save(filepath)
        filter_im = rgb_im.filter(ImageFilter.GaussianBlur(10))
        filter_im.save(filepath)

    def __str__(self):
        attrs = [self.size[0],
                 self.size[1],
                 self.count]
        attr_str = "\n".join(str(x) for x in attrs)
        points = json.dumps(self.points(),
                            default=lambda x: list(x))
        string = "{}\n{}".format(attr_str, points)
        return string


class HeatmapSeries(object):

    @staticmethod
    def new(manifest, interval, start):
        return HeatmapSeries(manifest, interval, start)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    def __init__(self, manifest, interval, start):
        super().__init__()
        self.manifest = manifest
        self.interval = interval
        self.start = start

        self.heatmaps = {}

    def subheatmaps(self):
        return [Heatmap.load(x) for x in self.heatmaps.values()]

    def sequence_start(self, dt):
        incoming = dt.replace(microsecond=0,
                              second=0)

        diff = incoming - self.start
        num_cycles = int(diff / self.interval)
        record_start = self.start + (num_cycles * self.interval)
        return record_start

    def _make_subheatmap(self, record_start, series_dir):
        heatmap = Heatmap.new(self.manifest)
        heatmap.period = heatmap.period.expand_to_include(record_start)
        datetimestamp = image.unparse_datetime(record_start)
        fmted_dtstamp = datetimestamp.replace(":", "-")
        fmted_dtstamp = fmted_dtstamp.replace(" ", "_")
        heatmap_filename = "{}.heatmap".format(fmted_dtstamp)
        fp = os.path.join(series_dir, heatmap_filename)
        heatmap.save(fp)
        self.heatmaps[record_start] = fp

    def select_subheatmap(self,
                          series_dir,
                          image_filepath):

        img = image.ImageData.create(self.manifest, image_filepath)
        dt = img.time_taken()

        # find out what interval this sequence of images
        # belongs in
        record_start = self.sequence_start(dt)

        # make sure this interval has a heatmap
        if record_start not in self.heatmaps:
            self._make_subheatmap(record_start, series_dir)

        heatmap_fp = self.heatmaps[record_start]
        return heatmap_fp


###############################################################################
# Heatmap Tools                                                               #
###############################################################################

def new_heatmap(heatmap_filepath, manifest):
    hm = Heatmap.new(manifest)
    hm.save(heatmap_filepath)


def record_heatmap(heatmap_filepath,
                   img_files,
                   period,
                   window_size=DEFAULT_WINDOW_SIZE,
                   color_thresh=DEFAULT_COLOR_THRESH):
    hm = Heatmap.load(heatmap_filepath)
    hm.record(img_files,
              period,
              window_size,
              color_thresh)
    hm.save(heatmap_filepath)


def view_heatmap(heatmap_filepath,
                 output_filepath):
    hm = Heatmap.load(heatmap_filepath)
    hm.write(output_filepath)


def project_heatmap(heatmap_filepath,
                    project_filepath,
                    desired_width,
                    moment=None):
    heatmap = Heatmap.load(heatmap_filepath)
    heatmap.project(project_filepath,
                    desired_width,
                    moment)
    heatmap.save(heatmap_filepath)


def overlay_heatmap(heatmap_filepath,
                    image_filepath,
                    output_filepath,
                    scale,
                    blur):
    hm = Heatmap.load(heatmap_filepath)
    img = Image.open(image_filepath)
    hm.overlay(img, output_filepath, scale, blur)


def new_series_heatmap(series_heatmap_filepath,
                       manifest,
                       interval,
                       start):
    series = HeatmapSeries.new(manifest, interval, start)
    series.save(series_heatmap_filepath)


def series_subheatmap(series_filepath,
                      image_filepath,
                      series_dir):
    series = HeatmapSeries.load(series_filepath)
    subheatmap_fp = series.select_subheatmap(series_dir, image_filepath)
    series.save(series_filepath)
    return subheatmap_fp


###############################################################################
# Helpers                                                                     #
###############################################################################

def image_obj_sequence(manifest, img_files, period):
    images = [image.ImageData.create(manifest, fp)
              for fp in img_files]
    images = trim_by_date(images, period)
    images = sort_by_date(images)
    return images


def trim_by_date(images, period):
    return [x for x in images
            if period.contains(x.time_taken())]


def sort_by_date(images):
    return sorted(images, key=lambda x: x.time_taken())


def windows(images, window_size):
    chunks = []
    window_idx_range = window_size - 1
    num_starting = len(images) - window_idx_range
    for start in range(num_starting):
        end = start + window_size
        chunk = images[start:end]
        chunks.append(chunk)
    return chunks


def extract_color_set(images, coord):
    return np.array([img[coord] for img in images])


def is_movement(images, coord,
                color_thresh=DEFAULT_COLOR_THRESH):
    '''determine if there is movement at a coordinate'''

    color_set = extract_color_set(images, coord)

    spread = np.ptp(color_set)
    return spread > color_thresh


###############################################################################
# Logging                                                                     #
###############################################################################

logger = logging.getLogger(__name__)


###############################################################################
# Command line                                                                #
###############################################################################

def parse_interval(sec):
    try:
        return timedelta(seconds=int(sec))
    except ValueError:
        msg = "interval must be a number of seconds"
        raise argparse.ArgumentTypeError(msg)


def parse_time(s):
    try:
        return image.parse_datetime(s)
    except ValueError:
        msg = "Illegal time format -- use {}"\
            .format(image.DATETIME_FMT)
        raise argparse.ArgumentTypeError(msg)


class MakeTimePeriodAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        time_period = TimePeriod(*values)
        setattr(namespace, self.dest, time_period)


def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="op")

    new_parser = subparsers.add_parser("new_heatmap",
                                       help="make new heatmap")
    new_parser.add_argument("heatmap_filepath",
                            help="file to contain heatmap")
    new_parser.add_argument("manifest",
                            type=cli.is_manifest_filepath,
                            help="file containing manifest")

    record_parser = subparsers.add_parser("record_heatmap",
                                          help="record imgs on heatmap")
    record_parser.add_argument("heatmap_filepath",
                               help="file containing heatmap")
    record_parser.add_argument("period",
                               help="time period to trim images",
                               nargs=2,
                               type=parse_time,
                               action=MakeTimePeriodAction)
    record_parser.add_argument("window_size",
                               help="size of sliding window",
                               type=int)
    record_parser.add_argument("color_thresh",
                               help="RGB magnitude of color difference",
                               type=int)
    record_parser.add_argument("images",
                               nargs="+",
                               help="Image files")

    view_heatmap = subparsers.add_parser("view_heatmap",
                                         help="see heatmap img")
    view_heatmap.add_argument("heatmap_filepath",
                              help="file containing heatmap")
    view_heatmap.add_argument("output_filepath",
                              help="file to contain heatmap img")

    project_parser = subparsers.add_parser("project_heatmap",
                                           help="project heatmap")
    project_parser.add_argument("heatmap_filename",
                                help="filename of heatmap")
    project_parser.add_argument("project_filename",
                                help="filename to project")
    project_parser.add_argument("desired_width",
                                type=int,
                                help="intended projection pixed width")

    overlay_parser = subparsers.add_parser("overlay_heatmap",
                                           help="overlay heatmap")
    overlay_parser.add_argument("heatmap_filepath",
                                help="filename of heatmap")
    overlay_parser.add_argument("image_filepath",
                                help="base image")
    overlay_parser.add_argument("output_filepath",
                                help="filepath of output")
    overlay_parser.add_argument("scale",
                                type=int,
                                help="scale of redshift")
    overlay_parser.add_argument("blur",
                                type=int,
                                help="radius of GaussianBlur")

    new_series_heatmap_parser = subparsers.add_parser("new_series_heatmap",
                                                      help="new series")
    new_series_heatmap_parser.add_argument("series_heatmap_filepath",
                                           help="file to contain series")
    new_series_heatmap_parser.add_argument("manifest",
                                           help="file containing manifest")
    new_series_heatmap_parser.add_argument("interval",
                                           type=parse_interval,
                                           help="seconds between heatmaps")
    new_series_heatmap_parser.add_argument("start",
                                           type=parse_time,
                                           help="starting point")

    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():

    log.start_log()

    args = get_args()

    if args.op == "new_heatmap":
        new_heatmap(args.heatmap_filepath,
                    Manifest.from_filepath(args.manifest))

    elif args.op == "record_heatmap":
        record_heatmap(args.heatmap_filepath,
                       args.images,
                       args.period,
                       args.window_size,
                       args.color_thresh)

    elif args.op == "view_heatmap":
        view_heatmap(args.heatmap_filepath,
                     args.output_filepath)

    elif args.op == "project_heatmap":
        project_heatmap(args.heatmap_filepath,
                        args.project_filepath,
                        args.desired_width)

    elif args.op == "overlay_heatmap":
        overlay_heatmap(args.heatmap_filepath,
                        args.image_filepath,
                        args.output_filepath,
                        args.scale,
                        args.blur)

    elif args.op == "new_series_heatmap":
        new_series_heatmap(args.series_heatmap_filepath,
                           Manifest.from_filepath(args.manifest),
                           args.interval,
                           args.start)


if __name__ == '__main__':
    main()
