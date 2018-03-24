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

    def write(self, filename):
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

    images = [Image.open(fp) for fp in image_filepaths]
    images = trim_by_date(images, delta)
    images = sort_by_date(images)

    image_sets = windows(images, window_size)

    heatmap = Heatmap(manifest)

    for image_set in image_sets:

        for coord in coordinates(dim):

            color_set = extract_color_set(images, coord)

            if is_movement(color_set):
                heatmap.add(coord)

    heatmap.write(output_filepath)


###############################################################################
# Helpers                                                                     #
###############################################################################

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
    parser.add_argument("--arg")
    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():

    args = get_args()


if __name__ == '__main__':
    main()
