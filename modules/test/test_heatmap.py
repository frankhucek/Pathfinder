
import sys
from pathlib import Path
cur_dir = Path(__file__).parents[0]
parent_dir = Path(__file__).parents[1]
if parent_dir not in sys.path:
    sys.path.insert(0, str(parent_dir))
if cur_dir not in sys.path:
    sys.path.insert(0, str(cur_dir))


###############################################################################
# Imports                                                                     #
###############################################################################

import os

from PIL import Image

from common import assert_close

from manifest import Manifest
from image import ImageData, WholeImageData

from datetime import datetime
from pytest import fixture
import pytest

from unittest.mock import MagicMock


###############################################################################
# Unit under test                                                             #
###############################################################################

import heatmap
from heatmap import TimePeriod, NullTimePeriod, Heatmap
from heatmap import CoordRange


###############################################################################
# Constants                                                                   #
###############################################################################

HEATMAP_IMAGE_DIR = "examples/heatmap"


###############################################################################
# Fixtures                                                                          #
###############################################################################

@fixture
def filepaths():
    return [os.path.join(HEATMAP_IMAGE_DIR, x)
            for x in os.listdir(HEATMAP_IMAGE_DIR)
            if x.endswith(".jpg")]


@fixture(scope='module')
def images():
    return [ImageData.create(None, x) for x in filepaths()]


@fixture(scope='module')
def filtered_images():
    f_images = heatmap.trim_by_date(images(), period())
    f_images = heatmap.sort_by_date(f_images)
    return f_images


@fixture
def period():
    return TimePeriod(datetime(2018, 3, 23, 21, 15, 25),
                      datetime(2018, 3, 23, 21, 15, 42))


@fixture
def first_time():
    return datetime(2018, 3, 23, 21, 15, 23)


@fixture
def last_time():
    return datetime(2018, 3, 23, 21, 15, 44)


@fixture
def point():
    return (2000, 1000)


@fixture()
def manifest():
    return Manifest.from_filepath("examples/manifest.json")


points = [
    ((2000, 1000), True),
    ((3000, 1000), True),
    ((1000, 2000), False),
    ((1500, 2000), False),
    ((2500, 250), False)
]


@fixture
def img_corners():
    return [[0, 0], [10, 0], [0, 10], [10, 10]]


@fixture
def coord_range():
    return CoordRange(img_corners())


###############################################################################
# TestCases                                                                   #
###############################################################################

def test_trim_by_date(images, period):
    trimmed = heatmap.trim_by_date(images, period)
    assert 5 == len(trimmed)


def test_trim_by_date_all(images, first_time, last_time):
    period = TimePeriod(first_time, last_time)
    trimmed = heatmap.trim_by_date(images, period)
    assert 7 == len(trimmed)


def test_trim_by_date_none(images, first_time, last_time):
    period = TimePeriod(last_time, first_time)
    trimmed = heatmap.trim_by_date(images, period)
    assert 0 == len(trimmed)


def test_sort_by_date(images):
    std = heatmap.sort_by_date(images)
    for v, w in pairwise(std):
        assert v.time_taken() <= w.time_taken()


def test_windows(images):
    windows = heatmap.windows(images, 3)
    assert 5 == len(windows)
    assert all(3 == len(x) for x in windows)


def test_windows_single(images):
    single_image_lst = [images[0]]
    windows = heatmap.windows(single_image_lst, 2)
    assert 0 == len(windows)


def test_coordinates():
    dim = (3, 4)
    coords = {(0, 0), (1, 0), (2, 0),
              (0, 1), (1, 1), (2, 1),
              (0, 2), (1, 2), (2, 2),
              (0, 3), (1, 3), (2, 3)}
    assert coords == WholeImageData.coordinates(None, dim)


def test_extract_color_set(images, point):
    color_set = heatmap.extract_color_set(images, point)
    assert 7 == len(color_set)


@pytest.mark.skip
@pytest.mark.parametrize("point,res",
                         points, ids=lambda x: str(x))
def test_is_movement_all(point, res, images):
    images = heatmap.trim_by_date(images, period())
    assert res == heatmap.is_movement(images, point,
                                      color_thresh=50)


def test_include_in_period(manifest, filtered_images):
    hm = Heatmap.new(manifest)
    hm.include_in_period(filtered_images)
    assert hm.period.start == datetime(2018, 3, 23, 21, 15, 26)
    assert hm.period.end == datetime(2018, 3, 23, 21, 15, 40)


def test_null_time_period(filtered_images):
    null_tp = NullTimePeriod()
    img = filtered_images[0]
    assert not null_tp.contains(img)
    tp = null_tp.expand_to_include(img.time_taken())
    assert tp.contains(img.time_taken())
    assert tp.start == img.time_taken()
    assert tp.end == img.time_taken()


def test_coord_range_corners(img_corners, coord_range):
    for corner in img_corners:
        assert coord_range.contains(corner)


def test_coord_range_inner(coord_range):
    assert coord_range.contains((5, 5))
    assert coord_range.contains((0, 5))
    assert coord_range.contains((5, 0))
    assert coord_range.contains((10, 5))
    assert coord_range.contains((5, 10))


def test_coord_range_outside(coord_range):
    assert not coord_range.contains((-10, -10))
    assert not coord_range.contains((20, 20))
    assert not coord_range.contains((11, 0))


###############################################################################
# Helper functions                                                            #
###############################################################################

def pairwise(lis):
    return zip(lis, lis[1:])


###############################################################################
# Asserts                                                                          #
###############################################################################



###############################################################################
# Main script                                                                 #
###############################################################################

if __name__ == '__main__':
    unittest.main()
