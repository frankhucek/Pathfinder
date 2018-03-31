
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

from manifest import Manifest
from common import assert_close

import mapping
from mapping import Geometry


###############################################################################
# Fixtures                                                                    #
###############################################################################

@fixture
def paper_manifest():
    return Manifest({
        "JobID": 11111,
        "geometry": {
            "height": 875,
            "width": 1167,
            "fov": [4.0, 3.0, 3.0],
            "upperleft": {
                "position": [357, 674],
                "distance": 83.25
            },
            "upperright": {
                "position": [832, 674],
                "distance": 83.25
            },
            "lowerleft": {
                "position": [255, 766],
                "distance": 61.25
            },
            "lowerright": {
                "position": [939, 768],
                "distance": 61.25
            }
        }
    })


@fixture
def image_corners():
    return [[357, 674],
            [832, 674],
            [255, 766],
            [939, 768]]


@fixture
def blueprint_coords():
    return [[0.0, 0.0],
            [42.0, 0.0],
            [0.0, 24.0],
            [42.0, 24.0]]


@fixture
def dim():
    return paper_manifest().dimensions()


@fixture
def geom():
    return Geometry.from_manifest(paper_manifest())


###############################################################################
# Test cases                                                                  #
###############################################################################

def test_bti_corners(paper_manifest, dim, geom, image_corners, blueprint_coords):

    # import pdb; pdb.set_trace()

    results = [mapping.blueprint_to_image(x, geom, dim)
               for x in blueprint_coords]

    # accurate within ~5 pixels
    assert_close(image_corners, results, atol=5)


def test_itb_corners(paper_manifest, dim, geom, blueprint_coords):

    corners = [mapping.image_to_blueprint(x, geom, dim)
               for x in paper_manifest.image_corners()]

    assert_close(blueprint_coords, corners, atol=0.5)
