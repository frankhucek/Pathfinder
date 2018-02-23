
###############################################################################
# Imports                                                                     #
###############################################################################


###############################################################################
# Unit under test                                                             #
###############################################################################

from .. import mapping

from pytest import fixture
import numpy as np


###############################################################################
# Constants                                                                   #
###############################################################################

FLOAT_TOLERANCE = 0.01


###############################################################################
# Fixtures                                                                    #
###############################################################################

@fixture
def pixel_coords():
    return [
        [0, 0],
        [0, 0.667],
        [0.333, 0.667],
        [0.333, 0]
    ]


@fixture
def image_corners():
    return [
        np.array([0, 0, 1]),
        np.array([0, 0.667, 1]),
        np.array([0.333, 0.667, 1]),
        np.array([0.333, 0, 1])
    ]


@fixture
def distances():
    return [3.0, 3.606, 3.742, 3.162]


@fixture
def map_corners():
    return [
        np.array([0.0, 0.0, 3.0]),
        np.array([0.0, 2.0, 3.0]),
        np.array([1.0, 2.0, 3.0]),
        np.array([1.0, 0.0, 3.0])
    ]


@fixture
def sample_geom():
    return mapping.Geometry(pixel_coords(), distances())


###############################################################################
# TestCases                                                                   #
###############################################################################

def test_transform_itb_middle(sample_geom):
    image_coord = [0.333, 0.165]
    blueprint_coord = [1.0, 0.5, 3.0]
    assert_close(blueprint_coord,
                 sample_geom.transform_itb(image_coord))


def test_transform_itb_corners(sample_geom, pixel_coords, map_corners):
    for pixel_coord, map_corner in zip(pixel_coords, map_corners):
        transformed = sample_geom.transform_itb(pixel_coord)
        assert_close(map_corner, transformed)


def test_compute_normal(map_corners):
    assert_close(np.array([0, 0, -1]),
                 mapping.Geometry.compute_normal(map_corners))


def test_project_corners(image_corners, distances, map_corners):
    mapped = mapping.Geometry.project_corners(image_corners,
                                              distances)
    assert_close(map_corners, mapped)


def test_add_zs(pixel_coords, image_corners):
    assert_close(image_corners,
                 mapping.Geometry.add_zs(pixel_coords))


###############################################################################
# Helpers                                                                          #
###############################################################################

def assert_close(a, b, atol=FLOAT_TOLERANCE):
    np.testing.assert_allclose(a, b, atol=atol)
