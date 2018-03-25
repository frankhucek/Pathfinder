
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

import os

from PIL import Image

from common import assert_close

from datetime import datetime
from pytest import fixture
import pytest


###############################################################################
# Unit under test                                                             #
###############################################################################

import heatmap
from heatmap import TimePeriod, Heatmap


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


@fixture
def images():
    return [Image.open(x) for x in filepaths()]


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
        assert heatmap.time_taken(v) <= heatmap.time_taken(w)


def test_windows(images):
    windows = heatmap.windows(images, 3)
    assert 4 == len(windows)
    assert all(3 == len(x) for x in windows)


def test_coordinates():
    dim = (3, 4)
    coords = {(0, 0), (1, 0), (2, 0),
              (0, 1), (1, 1), (2, 1),
              (0, 2), (1, 2), (2, 2),
              (0, 3), (1, 3), (2, 3)}
    assert coords == heatmap.coordinates(dim)


def test_extract_color_set(images):
    color_set = heatmap.extract_color_set(images, (0, 0))
    assert 7 == len(color_set)


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
