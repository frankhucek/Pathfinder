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

class ManifestError(Exception):
    """Error indicating malformed manifest

    Note that the fact that this error was _not_ thrown does
    not indicate the _values_ in the manifest are valid. This
    only ensures that all the necessary parts are present.
    """
    def __init__(self):
        super().__init__()


class Manifest(object):

    @staticmethod
    def from_filepath(manifest_filepath):
        with open(manifest_filepath) as manifest_file:
            return Manifest.from_file(manifest_file)

    @staticmethod
    def from_file(manifest_file):
        manifest_json = json.load(manifest_file)
        manifest = Manifest(manifest_json)
        manifest.verify()
        return manifest

    def verify(self):
        """Ensure that this manifest obj can call all req methods"""
        try:
            self.image_corners()
            self.corner_distances()
            self.dimensions()
            self.fov()
        except KeyError:
            raise ManifestError("Invalid manifest structure")

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

