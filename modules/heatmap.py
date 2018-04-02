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
DEFAULT_COLOR_VARIANCE_THRESH = 25

#Chosen arbitrarly, can test different chunk sizes and determine which is best
DEFAULT_CHUNK_WIDTH = 36
DEFAULT_CHUNK_HEIGHT = 36

#Values for analyzing RGB values
RED_INDEX = 0
GREEN_INDEX = 0
BLUE_INDEX = 0
LUMINOSITY_RED_VALUE = .299
LUMINOSITY_GREEN_VALUE = .587
LUMINOSITY_BLUE_VALUE =  .114

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

    def add_chunk(self, chunk):
        for coordinate in chunk.points:
            add(cordinate)

class PixelChunk(object):

    def __init__(self, points, width, height):
        super(PixelChunk, self).__init__()
        self.points = points
        self.width = width
        self.height = height

    #Why use this algorithm over a normal average
    #https://bit.ly/2E8XGPn
    def rgb_luminosity_average(self, image):
        average_red, average_green, average_blue = self.average_rgb_values(image)
        red_value = average_red * LUMINOSITY_RED_VALUE
        green_value = average_green * LUMINOSITY_GREEN_VALUE
        blue_value = average_blue * LUMINOSITY_BLUE_VALUE
        return red_value + green_value + blue_value

    def average_rgb_values(self, image):
        average_red = 0
        average_green = 0
        average_blue = 0
        for point in self.points:
            rgb = image.getpixel(point)
            average_red = average_red + rgb[RED_INDEX]
            average_green = average_green + rgb[GREEN_INDEX]
            average_blue = average_blue + rgb[BLUE_INDEX]
        average_red = average_red / len(self.points)
        average_green = average_green / len(self.points)
        average_blue = average_blue / len(self.points)
        return average_red, average_green, average_blue

    #why using a classic rgb average instead of luminosity
    #https://bit.ly/2E8XGPn (same link as rbg lumonisty)
    def rgb_variance(self, image):
        #+ (1/3)⋅(VarRed + VarGreen + VarBlue)
        var_red, var_green, var_blue = self.rgb_variance_values(image)
        variance = (1.0/3.0) * (var_red + var_green + var_blue)
        return variance + self.rgb_variance_rough_covariance_term()

    def rgb_variance_values(self, image):
        average_red, average_green, average_blue = self.average_rgb_values()
        var_red = 0
        var_green = 0
        var_blue =  0
        for point in self.points:
            rgb = image.getpixel(point)
            var_red = (average_red - rgb[RED_INDEX]) ** 2
            var_green = (average_green - rgb[GREEN_INDEX]) ** 2
            var_blue = (average_blue - rgb[BLUE_INDEX]) ** 2
        var_red = var_red / len(self.points)
        var_green = var_green / len(self.points)
        var_blue = var_blue / len(self.points)
        return var_red, var_green, var_blue

    def rgb_variance_rough_covariance_term(self):
        average_red, average_green, average_blue = self.average_rgb_values()
        value_one = (2.0/9.0) * ((average_red**2) + (average_green**2) +
                        (average_blue**2))
        value_two = ((average_red*average_green) + (average_red*average_blue) +
                    (average_blue*average_green)) * (2.0/9.0)
        return value_one - value_two

    def is_different(self, image, other_image):
        average_rgb_different = rgb_luminosity_difference(
                                self.rgb_luminosity_average(image),
                                self.rgb_luminosity_average(other_image))
        rgb_variance_different = rgb_luminosity_difference(
                                self.rgb_luminosity_variance(image),
                                self.rgb_luminosity_variance(other_image),
                                DEFAULT_COLOR_VARIANCE_THRESH)
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
        pixel_chunks = pixel_chunks(coordinates)
        for pixel_chunk in pixel_chunks
           if is_movement_in_chunk(images, pixel_chunk, color_thresh):
               heatmap.add_chunk(pixel_chunk)

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


def pixel_chunks(all_coordinates, chunk_width=DEFAULT_CHUNK_WIDTH,
            chunk_height=DEFAULT_CHUNK_HEIGHT):
    pixel_chunks = []
    for coord in all_coordinates:
        pixel_chunk = PixelChunk(coord, chunk_width, chunk_height)
        pixel_chunks.append(pixel_chunk)
    return pixel_chunks


def coordinates(dim):
    xs, ys = range(dim[0]), range(dim[1])
    return set(itertools.product(xs, ys))


def extract_color_set(images, coord):
    return [img.getpixel(coord) for img in images]


def are_different(color1, color2,
                  color_thresh=DEFAULT_COLOR_THRESH):
    difference = np.array(color2) - np.array(color1)
    return np.linalg.norm(difference) > color_thresh


def rgb_luminosity_difference(variance_one, variance_two,
                    color_thresh=DEFAULT_COLOR_THRESH):
    difference = variance_two - variance_two
    abs_difference = abs(difference)
    return difference > color_thresh


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

def is_movement_in_chunk(images, pixel_chunk,
                color_thresh=DEFAULT_COLOR_THRESH):
    color_set = extract_color_set(images, pixel_chunk)

    avg = np.average(color_set, 0)
    return any(are_different(avg, c, color_thresh)
               for c in color_set)

def extract_color_set_chunks(images, coord):
    return [img.getpixel(coord) for img in images]

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
