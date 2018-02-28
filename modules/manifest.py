'''Manifest manipulation module

Used to abstract manifest JSON. Use the Manifest class to read
a manifest JSON and extract its JSON info.
'''

###############################################################################
# Imports                                                                     #
###############################################################################

import json


###############################################################################
# Constants                                                                   #
###############################################################################

GEOMETRY = "geometry"

POSITION = "position"
DISTANCE = "distance"

HEIGHT = "height"
WIDTH = "width"

FOV = "fov"

CORNERS = [
    "upperleft",
    "upperright",
    "lowerleft",
    "lowerright"
]


###############################################################################
# Classes                                                                     #
###############################################################################

class Manifest(object):

    @staticmethod
    def from_file(manifest_filepath):
        with open(manifest_filepath) as manifest_file:
            manifest_json = json.load(manifest_file)
        manifest = Manifest(manifest_json)
        return manifest

    def __init__(self, manifest_json):
        super(Manifest, self).__init__()
        self.json = manifest_json

    def _geometry(self):
        return self.json[GEOMETRY]

    def _corners(self):
        geometry = self._geometry()
        return [geometry[corner] for corner in CORNERS]

    def _corner_attr(self, attr):
        return [x[attr] for x in self._corners()]

    def image_corners(self):
        return self._corner_attr(POSITION)

    def corner_distances(self):
        return self._corner_attr(DISTANCE)

    def _height(self):
        return self._geometry()[HEIGHT]

    def _width(self):
        return self._geometry()[WIDTH]

    def dimensions(self):
        return self._width(), self._height()

    def fov(self):
        return self._geometry()[FOV]

###############################################################################
# Helper functions                                                            #
###############################################################################

