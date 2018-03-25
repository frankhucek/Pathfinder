#! /usr/bin/env python3

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse

import numpy as np
from PIL import Image

from manifest import Manifest


###############################################################################
# Constants                                                                   #
###############################################################################

DEFAULT_WINDOW_SIZE = 10


###############################################################################
# Classes                                                                     #
###############################################################################

class Heatmap(object):

    def __init__(self, manifest):
        super(Heatmap, self).__init__()
        self.manifest
        self.size = manifest.dimensions()
        self.count = 0
        self.points = np.zeros(self.size)

    def add(coord):
        pass

    def project(self):
        pass


class BlueprintHeatmap(object):

    def __init__(self, size, scale, points):
        super(BlueprintHeatmap, self).__init__()
        self.size = size
        self.scale = scale
        self.ponts = points

    def write(self, filepath):
        pass


###############################################################################
# Heatmap Tools                                                               #
###############################################################################

def build_heatmap(image_filepaths,
                  output_filepath,
                  manifest,
                  delta,
                  window_size=DEFAULT_WINDOW_SIZE):

    dim = manifest.dimensions()

    images = image_obj_sequence(image_filepaths, delta)

    image_sets = windows(images, window_size)

    heatmap = Heatmap(manifest)

    for image_set in image_sets:

        for coord in coordinates(dim):

            color_set = extract_color_set(images, coord)

            if is_movement(color_set):
                heatmap.add(coord)

    blueprint_heatmap = heatmap.project()
    blueprint_heatmap.write(output_filepath)


###############################################################################
# Helpers                                                                     #
###############################################################################

def image_obj_sequence(image_filepaths, delta):
    images = [Image.open(fp) for fp in image_filepaths]
    images = trim_by_date(images, delta)
    images = sort_by_date(images)


def trim_by_date(images, delta):
    pass


def sort_by_date(images):
    pass


def windows(images, window_size):
    pass


def coordinates(manifest):
    pass


def extract_color_set(images, coord):
    pass


def is_movement(color_set):
    pass


###############################################################################
# Command line                                                                #
###############################################################################

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=["build_heatmap"])
    parser.add_argument("images",
                        action="append",
                        help="Image files")
    parser.add_argument("output",
                        help="name of output file")
    parser.add_argument("manifest",
                        help="manifest filepath")
    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():

    args = get_args()

    manifest = Manifest.from_file(args.manifest)

    if args.op == "build_heatmap":
        build_heatmap(args.images,
                      args.output,
                      manifest,
                      None)


if __name__ == '__main__':
    main()
