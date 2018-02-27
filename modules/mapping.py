#! /usr/bin/env python3

'''Mapping module

The mapping.py module provides several functions for transforming
between image and blueprint coordinates.

Example usage:
python3 mapping.py itb 350 450 examples/manifest.json

'''

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import numpy as np

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
        fov = manifest.fov()

        positions = center_img_coords(raw_positions, dim)

        geom = Geometry.make(fov, positions, distances)
        return geom

    @staticmethod
    def make(fov, image_corners, distances):
        """Geometry builder -- good for error checking"""
        return Geometry(fov, image_corners, distances)

    def __init__(self, fov, image_corners, distances):
        super(Geometry, self).__init__()
        self.fov = fov
        self.viewplane_corners = Geometry.to_view_planes(fov, image_corners)
        self.distances = distances

        self.map_corners = Geometry.project_corners(self.viewplane_corners,
                                                    fov,
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

    def orthonormals(self):
        m_a, m_b, m_c = self.map_corners[0:3]
        m_ab = m_b - m_a
        m_ac = m_c - m_a
        return m_ab, m_ac

    @staticmethod
    def project_corners(viewplane_corners, fov, distances):
        return [Geometry.project_corner(vc, fov, d)
                for vc, d in zip(viewplane_corners, distances)]

    @staticmethod
    def project_corner(viewplane_corner, fov, distance):
        scale = distance / norm(viewplane_corner)
        map_corner = scale * viewplane_corner
        return map_corner

    @staticmethod
    def to_view_planes(fov, image_coords):
        return [Geometry.to_view_plane(fov, image_coord)
                for image_coord in image_coords]

    @staticmethod
    def to_view_plane(fov, image_coord):
        vec = np.array(image_coord + [1])
        return vec * fov

    def s_to_view_plane(self, image_coord):
        return Geometry.to_view_plane(self.fov, image_coord)

    def _raw_transform_itb(self, image_coord):
        image_vector = self.s_to_view_plane(image_coord)
        scale = (np.dot(self.normal, self.top_left_map_corner) /
                 np.dot(self.normal, image_vector))
        blueprint_coord = scale * image_vector
        return blueprint_coord

    def transform_itb(self, image_coord):
        blueprint_coord = self._raw_transform_itb(image_coord)
        translated = blueprint_coord - self.top_left_map_corner

        # TODO potentially make the yaxis calculated?
        xaxis, yaxis = self.orthonormals()

        u = np.dot(translated, xaxis) / norm(xaxis)
        v = np.dot(translated, yaxis) / norm(yaxis)

        return [u, v]


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
    new_x = center(coord[0], dim[0])
    new_y = -center(coord[1], dim[1])
    return [new_x, new_y]


def center(value, normalization):
    half_normalization = normalization / 2
    return (value - half_normalization) / normalization


def norm(vec):
    return np.linalg.norm(vec)


def normalize(vec):
    return vec / norm(vec)


def format_coord(coord, precision):
    double_str = "{:0." + str(precision) + "f}"
    fmt_str = "{}\n{}".format(double_str, double_str)
    return fmt_str.format(*coord)


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
    parser.add_argument("-p", "--precision",
                        type=int,
                        default=3,
                        help="number of decimal points")
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

    print(format_coord(transformed, args.precision))


if __name__ == '__main__':
    main()
