
import sys
from pathlib import Path
cur_dir = Path(__file__).parents[0]
parent_dir = Path(__file__).parents[1]
if parent_dir not in sys.path:
    sys.path.append(str(parent_dir))
if cur_dir not in sys.path:
    sys.path.append(str(cur_dir))


###############################################################################
# Imports                                                                     #
###############################################################################

from pytest import fixture
import pytest
import argparse
import numpy as np

from unittest.mock import patch, MagicMock

from manifest import Manifest
from common import assert_close


###############################################################################
# Unit under test                                                             #
###############################################################################

import mapping
from mapping import Geometry


###############################################################################
# Fixtures                                                                    #
###############################################################################

@fixture
def fov():
    return [1.0, 1.0, 1.0]


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
    return Geometry(fov(), pixel_coords(), distances())


@fixture
def manifest():
    return Manifest({
        "JobID": 12345,
        "geometry": {
            "height": 1000,
            "width": 1000,
            "fov": [1.0, 1.0, 1.0],
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
    })


@fixture
def dim():
    return manifest().dimensions()


@fixture
def geom():
    return Geometry.from_manifest(manifest())


def fake_parse(arg_strings):
    class MockParser(argparse.ArgumentParser):
        def parse_args(self):
            return super().parse_args(arg_strings)
    argparse_mock = MagicMock(ArgumentParser=MockParser)

    with patch("mapping.argparse", argparse_mock):
        args = mapping.get_args()
    return args


###############################################################################
# TestCases                                                                   #
###############################################################################

def test_uncenter_img_coords(dim, pixel_coords):

    results = [[500, 500],
               [1000, 500],
               [500, 750],
               [1000, 750]]

    for res, coord in zip(results, pixel_coords):
        assert_close(res, mapping.uncenter_img_coord(coord, dim))


def test_identical_image_corners(fov, distances):
    image_corners = [[-0.24, 0.34],
                     [0.1, 0.4],
                     [-0.14, -0.2],
                     [-0.14, -0.2]]
    with pytest.raises(ValueError):
        Geometry.make(fov, image_corners, distances)


def test_geometry_neg_distances(fov, image_corners):
    with pytest.raises(ValueError):
        Geometry.make(fov, image_corners, [3.0, -4.3, 0.0])


def test_geometry_neg_fov(image_corners, distances):
    with pytest.raises(ValueError):
        Geometry.make([-3.0, 2.0, 1.0], image_corners, distances)


def test_geometry_zero_fov():
    with pytest.raises(ValueError):
        Geometry.make([0.0, 2.0, 1.0], image_corners, distances)


def test_itb_negative_coords(geom, dim):
    pixel_coord = [-5, -5]
    with pytest.raises(ValueError):
        mapping.image_to_blueprint(pixel_coord, geom, dim)


def test_itb_oob_coords(geom, dim):
    pixel_coord = [9999999, 99999999]
    with pytest.raises(ValueError):
        mapping.image_to_blueprint(pixel_coord, geom, dim)


def test_from_file(geom, dim):

    pixel_coord = [350, 450]
    blueprint_coord = [2, 4]

    transformed = mapping.image_to_blueprint(pixel_coord,
                                             geom,
                                             dim)

    assert_close(blueprint_coord, transformed)


def test_center_img_coords(dim, manifest):
    raw = manifest.image_corners()

    translated = mapping.center_img_coords(raw, dim)

    expected = [[-0.25, 0.25],
                [0.25, 0.25],
                [-0.25, -0.25],
                [0.25, -0.25]]

    assert_close(expected, translated)


def test_center_img_coord_one(dim):

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
    fov = [1.0, 1.0, 1.0]
    geom = Geometry(fov, pixel_coords, distances)

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


def test_transform_itb_corners(sample_geom,
                               pixel_coords,
                               map_corners):
    # import pdb; pdb.set_trace()
    for pixel_coord, map_corner in zip(pixel_coords, map_corners):
        transformed = sample_geom.transform_itb(pixel_coord)
        assert_close(map_corner, transformed)


def test_compute_normal(raw_3d):
    assert_close(np.array([0, 0, -1]),
                 Geometry.compute_normal(raw_3d))


def test_project_corners(image_corners, distances, raw_3d, fov):
    mapped = Geometry.project_corners(image_corners,
                                      fov,
                                      distances)
    assert_close(raw_3d, mapped)


def test_format_coord():
    assert "1.00\n2.00" == mapping.format_coord([1.0, 2.0], 2)


def test_cli_nominal():
    arg_strings = ["itb", "350", "450", "examples/manifest.json"]
    args = fake_parse(arg_strings)

    assert args.op == "itb"
    assert args.coord == [350, 450]
    assert args.manifest == "examples/manifest.json"


def test_cli_invalid_op():
    arg_strings = ["fake", "350", "450", "examples/manifest.json"]
    with pytest.raises(SystemExit):
        fake_parse(arg_strings)


def test_cli_non_int_coord():
    arg_strings = ["itb", "a", "450", "examples/manifest.json"]
    with pytest.raises(SystemExit):
        fake_parse(arg_strings)


def test_cli_non_file_manifest():
    arg_strings = ["itb", "350", "450", "NOT_A_FILE"]
    with pytest.raises(SystemExit):
        fake_parse(arg_strings)
