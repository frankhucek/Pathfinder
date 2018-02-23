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
    def from_file(manifest):
        """tool for making a Geometry object from a manifest"""
        pass

    @staticmethod
    def make(image_corners, distances):
        """Geometry builder -- good for error checking"""
        pass

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
        return blueprint_coord


###############################################################################
# Mapping Functions                                                           #
###############################################################################

def image_to_blueprint(image_coord, geometry):
    '''Map image coordinates to blueprint coordinates

    Input: (x,y)
    '''
    blueprint_coord = geometry.transform_itb(image_coord)
    return blueprint_coord


def blueprint_to_image(blueprint_coord):
    image_coord = blueprint_coord
    return image_coord


###############################################################################
# Helper functions                                                            #
###############################################################################

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
    geometry = Geometry.from_file(args.manifest)

    if args.op == BLUEPRINT_TO_IMAGE:
        transformed = blueprint_to_image(coord, geometry)
    elif args.op == IMAGE_TO_BLUEPRINT:
        transformed = image_to_blueprint(coord, geometry)

    print(format_coord(transformed))


if __name__ == '__main__':
    main()
