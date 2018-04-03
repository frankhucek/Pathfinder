#! /usr/bin/env python3

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import itertools
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

#Chosen arbitrarly, can test different chunk sizes and determine which is best
DEFAULT_CHUNK_WIDTH = 36
DEFAULT_CHUNK_HEIGHT = 36

DATETIME_FMT = "%Y:%m:%d %H:%M:%S"
DATETIME_EXIF = 36867


###############################################################################
# Classes                                                                     #
###############################################################################

class ImageData(object):
    """obj that provides data about an image"""

    def __init__(self, manifest):
        super().__init__()
        self.manifest = manifest

    @classmethod
    def create(manifest, filepath):
        raise NotImplementedError("Implement in subclass")

    def time_taken(self):
        raise NotImplementedError("Implement in subclass")

    def register(self, heatmap, coord):
        raise NotImplementedError("Implement in subclass")

    @staticmethod
    def coordinates(self, dim):
        raise NotImplementedError("Implement in subclass")

    def at(self, coord):
        raise NotImplementedError("Implement in subclass")


class WholeImageData(ImageData):

    def __init__(self, manifest, img):
        super().__init__(manifest)
        self._img = img
        self._pa = img.load()

    @classmethod
    def create(cls, manifest, filepath):
        img = Image.open(filepath)
        return cls(manifest, img)

    def time_taken(self):
        dt_str = self._img._getexif()[DATETIME_EXIF]
        dt_obj = datetime.strptime(dt_str, DATETIME_FMT)
        return dt_obj

    def register(self, heatmap, coord):
        heatmap.add(coord)

    @staticmethod
    def coordinates(dim):
        xs, ys = range(dim[0]), range(dim[1])
        return set(itertools.product(xs, ys))

    def at(self, coord):
        return self._pa[coord]


class ChunkImageData(ImageData):
    pass


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
        width, height = manifest.dimensions()
        points = np.zeros((height, width))
        return Heatmap(manifest, points)

    def __init__(self, manifest, points):
        super(Heatmap, self).__init__()
        self.manifest = manifest
        self.size = np.flip(manifest.dimensions(), 0)
        self.count = 0
        self._points = points

    def add(self, coord):
        self.count += 1
        self.set(coord, self.at(coord) + 1)

    def set(self, coord, val):
        self._points[self._flip(coord)] = val

    def at(self, coord):
        return self._points[self._flip(coord)]

    def _flip(self, coord):
        x, y = coord
        return y, x

    def points(self):
        return self._points / np.max(self._points)

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

    def add_chunk(self, chunk):
        for coordinate in chunk.points:
            add(cordinate)

class PixelChunk(object):

    def __init__(self, image, points, width, height):
        super(PixelChunk, self).__init__()
        self.image = image
        self.points = points
        self.width = width
        self.height = height

    def rgb_average(self):
        val = 0
        for point in self.points:
            val = val + (self.image.getpixel(point) ** 2)
        return math.sqrt(val)

    def rgb_variance(self):
        pass

    def is_different(self, other_chunk):
        average_rgb_different = are_different(rgb_average(),
                        other_chunk.rgb_average())
        rgb_variance_different = variance_difference(rgb_variance(),
                        other_chunk.rgb_variance())
        return average_rgb_different or rgb_variance_different


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

        all_coordinates = coordinates(dim)
        #pixel_chunks = pixel_chunks(coordinates)
        #for pixel_chunk in pixel_chunks
        #   if is_movement(images, pixel_chunk, color_thresh):
        #       heatmap.add_chunk(pixel_chunk)
        for coord in all_coordinates:

            if is_movement(image_set, coord, color_thresh):
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
    images = [im.load() for im in images]
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


def chunks(image, all_coordinates, chunk_width=DEFAULT_CHUNK_WIDTH,
            chunk_height=DEFAULT_CHUNK_HEIGHT):
    pixel_chunks = []
    for coord in all_coordinates:
        pixel_chunk = PixelChunk(image, coord, chunk_width, chunk_height)
        pixel_chunks.append(pixel_chunk)
    return pixel_chunks


def coordinates(dim):
    xs, ys = range(dim[0]), range(dim[1])
    return set(itertools.product(xs, ys))


def extract_color_set(images, coord):
    return np.array([img[coord] for img in images])


def are_different(color1, color2,
                  color_thresh=DEFAULT_COLOR_THRESH):
    difference = np.array(color2) - np.array(color1)
    return np.linalg.norm(difference) > color_thresh


def variance_difference(variance_one, variance_two):
    pass


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

    spread = np.ptp(color_set)
    return spread > color_thresh


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
