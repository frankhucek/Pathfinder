#! /usr/bin/env python3

'''Mapping module

The mapping.py module provides several functions for transforming
between image and blueprint coordinates.
'''

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import numpy as np
from copy import deepcopy

from manifest import Manifest


###############################################################################
# Constants                                                                   #
###############################################################################

BLUEPRINT_TO_IMAGE = "bti"
IMAGE_TO_BLUEPRINT = "itb"

OPERATIONS = [
    BLUEPRINT_TO_IMAGE,
    IMAGE_TO_BLUEPRINT
]


###############################################################################
# Classes                                                                     #
###############################################################################

class Geometry(object):
    """Describes camera geometry"""

    @staticmethod
    def from_manifest(manifest):
        """tool for making a Geometry object from a manifest"""
        distances = manifest.corner_distances()
        raw_positions = manifest.image_corners()
        dim = manifest.dimensions()

        positions = center_img_coords(raw_positions, dim)

        geom = Geometry.make(positions, distances)
        return geom

    @staticmethod
    def make(image_corners, distances):
        """Geometry builder -- good for error checking"""
        return Geometry(image_corners, distances)

    def __init__(self, image_corners, distances):
        super(Geometry, self).__init__()
        self.image_corners = Geometry.add_zs(image_corners)
        self.distances = distances

        self.map_corners = Geometry.project_corners(self.image_corners,
                                                    distances)

        self.top_left_map_corner = self.map_corners[0]

        self.normal = Geometry.compute_normal(self.map_corners)

    @staticmethod
    def compute_normal(map_corners):
        m_a, m_b, m_c = map_corners[0:3]
        m_ab = m_b - m_a
        m_ac = m_c - m_a
        n = normalize(np.cross(m_ab, m_ac))
        return n

    @staticmethod
    def add_zs(pairs):
        return [Geometry.add_z(pair) for pair in pairs]

    @staticmethod
    def add_z(pair):
        return np.array(pair + [1])

    @staticmethod
    def project_corners(image_corners, distances):
        return [Geometry.project_corner(ic, d)
                for ic, d in zip(image_corners, distances)]

    @staticmethod
    def project_corner(image_corner, distance):
        scale = distance / norm(image_corner)
        map_corner = scale * image_corner
        return map_corner

    def transform_itb(self, image_coord):
        image_vector = Geometry.add_z(image_coord)
        scale = (np.dot(self.normal, self.top_left_map_corner) /
                 np.dot(self.normal, image_vector))
        blueprint_coord = scale * image_vector
        translated = self.translate_blueprint(blueprint_coord)
        reflected = self.reflect_blueprint(translated)
        return reflected

    def translate_blueprint(self, coord):
        coord_xy = self.xy(coord)
        top_left_xy = self.xy(self.top_left_map_corner)
        return coord_xy - top_left_xy

    def reflect_blueprint(self, coord):
        reflected = deepcopy(coord)
        multiplicand = 1 if reflected[1] == 0 else -1
        reflected[1] *= multiplicand
        return reflected

    @staticmethod
    def xy(three_d_coord):
        return three_d_coord[0:2]


###############################################################################
# Mapping Functions                                                           #
###############################################################################

def image_to_blueprint(pixel_coord, geom, dim):
    '''Map image coordinates to blueprint coordinates

    Input: (x,y)
    '''
    image_coord = center_img_coord(pixel_coord, dim)
    blueprint_coord = geom.transform_itb(image_coord)
    return blueprint_coord


def blueprint_to_image(blueprint_coord, geom, dim):
    image_coord = blueprint_coord
    return image_coord


###############################################################################
# Helper functions                                                            #
###############################################################################

def center_img_coords(coords, dim):
    return [center_img_coord(x, dim) for x in coords]


def center_img_coord(coord, dim):
    return [center(c, d) for c, d in zip(coord, dim)]


def center(value, normalization):
    return (value - normalization) / normalization


def norm(vec):
    return np.linalg.norm(vec)


def normalize(vec):
    return vec / norm(vec)


def format_coord(coord):
    return "{}\n{}".format(*coord)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=OPERATIONS,
                        help="Mapping operation")
    parser.add_argument("coord",
                        type=float,
                        nargs=2,
                        help="coordinates to map")
    parser.add_argument("manifest",
                        help="job_manifest_file")
    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():

    args = get_args()

    coord = args.coord
    manifest = Manifest.from_file(args.manifest)
    dim = manifest.dimensions()
    geometry = Geometry.from_manifest(manifest)

    if args.op == BLUEPRINT_TO_IMAGE:
        transformed = blueprint_to_image(coord, geometry, dim)
    elif args.op == IMAGE_TO_BLUEPRINT:
        transformed = image_to_blueprint(coord, geometry, dim)

    print(format_coord(transformed))


if __name__ == '__main__':
    main()
