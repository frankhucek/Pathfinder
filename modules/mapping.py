#! /usr/bin/env python3

'''Mapping module

The mapping module provides a 1-1 mapping between coordinates in
a job's image coordinate frame and coordinates in a job's blueprint
coordinate frame. Image space coordinates are in the form (x,y),
where x and y are the number of pixels between a given point and the
upper left corner of the images. Blueprint space coordinates are
in the form (u,v), where the point u,v is a real world position
measured from the upper left of the job's field of interest.

NOTE: currently, the only allowed field of interest geometry is
a rectangle. Fundamentally, the field of interest could be any
convex polygon. However, the implementation can't yet support it.

The mapping.py module provides several functions for transforming
between image and blueprint coordinates. This mapping API can be
found in the Mapping Functions section of this file.

Most of the mapping API operations are implemented using a
Geometry object, though users of the API should consider this class
an implementation detail.

The mapping API can also be accessed using the command line interface
defined in this file.

Example usage:
python3 mapping.py itb 350 450 examples/manifest.json

'''

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import numpy as np

from itertools import combinations

from manifest import Manifest
import cli


###############################################################################
# Constants                                                                   #
###############################################################################

BLUEPRINT_TO_IMAGE = "bti"
IMAGE_TO_BLUEPRINT = "itb"


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

        if any(x <= 0 for x in fov):
            raise ValueError("All FOV values must be positive")
        elif any_negative(distances):
            raise ValueError("All corner distances must be positive")
        elif any_same(image_corners):
            raise ValueError("Cannot have overlapping corners")

        return Geometry(fov, image_corners, distances)

    def __init__(self, fov, image_corners, distances):
        super(Geometry, self).__init__()
        self.fov = np.array(fov)
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

    def collapse_to_viewplane(self, vec):
        divisor = vec[2] / self.fov[2]
        return vec / divisor

    @staticmethod
    def along_axis(pos, axis):
        return (pos / norm(axis)) * axis

    def transform_bti(self, blueprint_coord):

        xaxis, yaxis = self.orthonormals()

        blueprint_vec = sum(self.along_axis(pos, axis) for pos, axis
                            in zip(blueprint_coord, self.orthonormals()))

        projected_vec = self.top_left_map_corner + blueprint_vec

        # divide by z to arrive on viewplane
        viewplane_vec = self.collapse_to_viewplane(projected_vec)

        # divide by FOV to arrive on image
        image_vec = np.divide(viewplane_vec, self.fov)

        # remove z to get image coordinates
        image_coord = image_vec[0:2]

        return image_coord


###############################################################################
# Mapping Functions                                                           #
###############################################################################

def image_to_blueprint(pixel_coord, geom, dim):
    '''Map image coordinates to blueprint coordinates'''

    if any_negative(pixel_coord):
        raise ValueError("All pixel positions must be positive")
    elif pixel_out_of_bounds(pixel_coord, dim):
        raise ValueError("Pixel positions must be inside img dimensions")

    image_coord = center_img_coord(pixel_coord, dim)
    blueprint_coord = geom.transform_itb(image_coord)
    return blueprint_coord


def blueprint_to_image(blueprint_coord, geom, dim):
    '''Map blueprint coordinates to image coordinates'''

    image_coord = geom.transform_bti(blueprint_coord)
    image_coord = uncenter_img_coord(image_coord, dim)
    return image_coord


###############################################################################
# Validation                                                                  #
###############################################################################

def any_negative(lis):
    return any(x < 0 for x in lis)


def pixel_out_of_bounds(pixel_coord, dim):
    return any(x > y for x, y in zip(pixel_coord, dim))


def any_same(lis):
    return any(x == y for x, y in combinations(lis, 2))


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


def uncenter_img_coord(coord, dim):
    new_x = uncenter(coord[0], dim[0], 1)
    new_y = uncenter(coord[1], dim[1], -1)
    return [new_x, new_y]


def uncenter(value, normalization, direction):
    offset = normalization / 2
    difference = (value * normalization) * direction
    result = offset + difference
    return result


def norm(vec):
    return np.linalg.norm(vec)


def normalize(vec):
    return vec / norm(vec)


def format_coord(coord, precision):
    double_str = "{:0." + str(precision) + "f}"
    fmt_str = "{}\n{}".format(double_str, double_str)
    return fmt_str.format(*coord)


###############################################################################
# CLI                                                                         #
###############################################################################

OPERATIONS = {
    BLUEPRINT_TO_IMAGE: blueprint_to_image,
    IMAGE_TO_BLUEPRINT: image_to_blueprint
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=OPERATIONS.keys(),
                        help="Mapping operation")
    parser.add_argument("coord",
                        type=float,
                        nargs=2,
                        help="coordinates to map")
    parser.add_argument("manifest",
                        type=cli.is_manifest_filepath,
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
    manifest = Manifest.from_filepath(args.manifest)
    dim = manifest.dimensions()
    geometry = Geometry.from_manifest(manifest)

    op = OPERATIONS[args.op]
    transformed = op(coord, geometry, dim)

    print(format_coord(transformed, args.precision))


if __name__ == '__main__':
    main()
