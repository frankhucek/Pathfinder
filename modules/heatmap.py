#! /usr/bin/env python3

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import itertools
import math
import json

from datetime import datetime

import numpy as np
from PIL import Image

from manifest import Manifest
import cli


###############################################################################
# Constants                                                                   #
###############################################################################

DEFAULT_WINDOW_SIZE = 2
DEFAULT_COLOR_THRESH = 50

DATETIME_FMT = "%Y:%m:%d %H:%M:%S"
DATETIME_EXIF = 36867


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


class Heatmap(object):

    @staticmethod
    def new(manifest):
        points = np.zeros(manifest.dimensions())
        return Heatmap(manifest, points)

    def __init__(self, manifest, points):
        super(Heatmap, self).__init__()
        self.manifest = manifest
        self.size = manifest.dimensions()
        self.count = 0
        self._points = points

    def add(self, coord):
        self.count += 1
        self._points[coord] += 1

    def points(self):
        return self._points / np.max(self._points)
        # return self._points

    def project(self):
        pass

    def write(self, filepath):
        with open(filepath, 'w') as f:
            f.write(str(self))
        write_points = self.points() * 255
        uint_points = write_points.astype('uint8')
        im = Image.fromarray(uint_points, 'L')
        im.save("heatmap.bmp")

    def __str__(self):
        attrs = [self.size[0],
                 self.size[1],
                 self.count]
        attr_str = "\n".join(str(x) for x in attrs)
        points = json.dumps(self.points(),
                            default=lambda x: list(x))
        string = "{}\n{}".format(attr_str, points)
        return string


###############################################################################
# Heatmap Tools                                                               #
###############################################################################

def build_heatmap(image_filepaths,
                  output_filepath,
                  manifest,
                  period,
                  window_size=DEFAULT_WINDOW_SIZE,
                  color_thresh=DEFAULT_COLOR_THRESH):

    dim = manifest.dimensions()

    images = image_obj_sequence(image_filepaths, period)

    image_sets = windows(images, window_size)

    heatmap = Heatmap.new(manifest)

    for idx, image_set in enumerate(image_sets):

        print("image_set: {}".format(idx))

        for coord in coordinates(dim):

            if is_movement(images, coord, color_thresh):
                heatmap.add(coord)

    heatmap.write(output_filepath)


###############################################################################
# Helpers                                                                     #
###############################################################################

def time_taken(img):
    dt_str = img._getexif()[DATETIME_EXIF]
    dt_obj = datetime.strptime(dt_str, DATETIME_FMT)
    return dt_obj


def image_obj_sequence(image_filepaths, period):
    images = [Image.open(fp) for fp in image_filepaths]
    images = trim_by_date(images, period)
    images = sort_by_date(images)
    return images


def trim_by_date(images, period):
    return [x for x in images
            if period.contains(time_taken(x))]


def sort_by_date(images):
    return sorted(images, key=time_taken)


def windows(images, window_size):
    chunks = []
    for start in range(len(images) - window_size):
        end = start + window_size
        chunk = images[start:end]
        chunks.append(chunk)
    return chunks


def coordinates(dim):
    xs, ys = range(dim[0]), range(dim[1])
    return set(itertools.product(xs, ys))


def extract_color_set(images, coord):
    return [img.getpixel(coord) for img in images]


def are_different(color1, color2,
                  color_thresh=DEFAULT_COLOR_THRESH):
    difference = np.array(color2) - np.array(color1)
    return np.linalg.norm(difference) > color_thresh


def is_movement(images, coord,
                color_thresh=DEFAULT_COLOR_THRESH):
    '''determine if there is movement at a coordinate

    computes the average color among the color set. Then,
    checks if any individual color in the set exceeds a
    certain RGB magnitude difference from the average.
    If so, it returns true, indicating there is a
    movement at this coordinate. Should run in time
    linear to the window size.
    '''
    color_set = extract_color_set(images, coord)

    avg = np.average(color_set, 0)
    return any(are_different(avg, c, color_thresh)
               for c in color_set)


###############################################################################
# Command line                                                                #
###############################################################################

def parse_time(s):
    try:
        return datetime.strptime(s, DATETIME_FMT)
    except ValueError:
        msg = "Illegal time format -- use {}".format(DATETIME_FMT)
        raise argparse.ArgumentTypeError(msg)


class MakeTimePeriodAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        time_period = TimePeriod(*values)
        setattr(namespace, self.dest, time_period)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=["build_heatmap"])
    parser.add_argument("output",
                        help="name of output file")
    parser.add_argument("manifest",
                        help="manifest filepath",
                        type=cli.is_manifest_filepath)
    parser.add_argument("period",
                        help="time period to trim images",
                        nargs=2,
                        type=parse_time,
                        action=MakeTimePeriodAction)
    parser.add_argument("window_size",
                        help="size of sliding window",
                        type=int)
    parser.add_argument("color_thresh",
                        help="RGB magnitude of color difference",
                        type=int)
    parser.add_argument("images",
                        nargs="+",
                        help="Image files")
    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():

    args = get_args()

    manifest = Manifest.from_filepath(args.manifest)

    if args.op == "build_heatmap":
        build_heatmap(args.images,
                      args.output,
                      manifest,
                      args.period,
                      args.window_size,
                      args.color_thresh)


if __name__ == '__main__':
    main()
