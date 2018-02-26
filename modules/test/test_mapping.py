
import sys
from pathlib import Path
parent_dir = Path(__file__).parents[1]
if parent_dir not in sys.path:
    sys.path.append(str(parent_dir))

###############################################################################
# Imports                                                                     #
###############################################################################

from pytest import fixture
import numpy as np

from unittest.mock import patch, MagicMock

from manifest import Manifest


###############################################################################
# Unit under test                                                             #
###############################################################################

import mapping
from mapping import Geometry


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
        [0.5, 0],
        [0, -0.25],
        [0.5, -0.25]
    ]


@fixture
def image_corners():
    return [
        np.array([0, 0, 1]),
        np.array([0.5, 0, 1]),
        np.array([0, -0.25, 1]),
        np.array([0.5, -0.25, 1])
    ]


@fixture
def distances():
    return [2, 2.236, 2.06155, 2.291288]


@fixture
def raw_3d():
    return [
        np.array([0.0, 0.0, 2.0]),
        np.array([1.0, 0.0, 2.0]),
        np.array([0.0, -0.5, 2.0]),
        np.array([1.0, -0.5, 2.0])
    ]


@fixture
def map_corners():
    return [
        np.array([0.0, 0.0]),
        np.array([1.0, 0.0]),
        np.array([0.0, 0.5]),
        np.array([1.0, 0.5])
    ]


@fixture
def sample_geom():
    return Geometry(pixel_coords(), distances())


@fixture
def manifest():
    return {
        "JobID": 12345,
        "geometry": {
            "height": 1000,
            "width": 1000,
            "upperleft": {
                "position": [250, 250],
                "distance": 21.21320344
            },
            "upperright": {
                "position": [750, 250],
                "distance": 21.21320344
            },
            "lowerleft": {
                "position": [250, 750],
                "distance": 21.21320344
            },
            "lowerright": {
                "position": [750, 750],
                "distance": 21.21320344
            }
        }
    }


###############################################################################
# TestCases                                                                   #
###############################################################################

def test_from_file(manifest):
    man = Manifest(manifest)
    dim = man.dimensions()
    geom = Geometry.from_manifest(man)

    pixel_coord = [350, 450]
    blueprint_coord = [2, 4]

    transformed = mapping.image_to_blueprint(pixel_coord,
                                             geom,
                                             dim)

    assert_close(blueprint_coord, transformed)


def test_center_img_coords(manifest):
    man = Manifest(manifest)
    dim = man.dimensions()

    raw = man.image_corners()

    translated = mapping.center_img_coords(raw, dim)

    expected = [[-0.25, 0.25],
                [0.25, 0.25],
                [-0.25, -0.25],
                [0.25, -0.25]]

    assert_close(expected, translated)


def test_center_img_coord_one(manifest):
    man = Manifest(manifest)
    dim = man.dimensions()

    raw = [250, 250]
    translated = mapping.center_img_coord(raw, dim)
    expected = [-0.25, 0.25]

    assert_close(expected, translated)


def test_transform_itb_translated_corner():
    pixel_coords = [[-0.25, 0.25],
                    [0.25, 0.25],
                    [-0.25, -0.25],
                    [0.25, -0.25]]
    distances = [21.21320344] * 4
    geom = Geometry(pixel_coords, distances)

    transformed = [geom.transform_itb(x) for x in pixel_coords]

    map_coords = [[0, 0],
                  [10, 0],
                  [0, 10],
                  [10, 10]]

    assert_close(map_coords, transformed)


def test_transform_itb_middle(sample_geom):
    image_coord = [0.25, -0.125]
    blueprint_coord = [0.5, 0.25]
    assert_close(blueprint_coord,
                 sample_geom.transform_itb(image_coord))


def test_transform_itb_corners(sample_geom, pixel_coords, map_corners):
    for pixel_coord, map_corner in zip(pixel_coords, map_corners):
        transformed = sample_geom.transform_itb(pixel_coord)
        assert_close(map_corner, transformed)


def test_compute_normal(raw_3d):
    assert_close(np.array([0, 0, -1]),
                 Geometry.compute_normal(raw_3d))


def test_project_corners(image_corners, distances, raw_3d):
    mapped = Geometry.project_corners(image_corners,
                                              distances)
    assert_close(raw_3d, mapped)


def test_add_zs(pixel_coords, image_corners):
    assert_close(image_corners,
                 Geometry.add_zs(pixel_coords))


###############################################################################
# Helpers                                                                          #
###############################################################################

def assert_close(a, b, atol=FLOAT_TOLERANCE):
    np.testing.assert_allclose(a, b, atol=atol)
