'''image module

The image module provides a level of abstraction between actual
image files and the level of detail required to produce a heatmap
from them.

Mainly, this lets the heatmap module use either image files (.jpg)
or prechunked image files (.txt) without having to know which one
it is using.

Also defines the datetime conventions for checking the dates of
images.
'''

###############################################################################
# Imports                                                                     #
###############################################################################

import os
import itertools
from datetime import datetime

from PIL import Image

from chunk import PixelChunk

###############################################################################
# Constants                                                                   #
###############################################################################

DATETIME_FMT = "%Y:%m:%d %H:%M:%S"
DATETIME_EXIF = 36867


###############################################################################
# Classes                                                                     #
###############################################################################

class ImageData(object):
    """obj that provides data about an image"""

    def __init__(self, manifest):
        super().__init__()
        self.manifest = manifest

    @staticmethod
    def sub_type(filepaths):

        extensions = [os.path.splitext(fp)[1] for fp in filepaths]

        if any(x != extensions[0] for x in extensions):
            raise ValueError("Mismatched file types!")

        if extensions[0] == ".jpg":
            return WholeImageData
        else:
            return ChunkImageData

    @staticmethod
    def create(manifest, filepath):
        sub_type = ImageData.sub_type([filepath])
        return sub_type.create(manifest, filepath)

    def time_taken(self):
        raise NotImplementedError("Implement in subclass")

    @staticmethod
    def register(self, heatmap, coord):
        raise NotImplementedError("Implement in subclass")

    @staticmethod
    def coordinates(manifest, dim):
        raise NotImplementedError("Implement in subclass")

    def at(self, coord):
        raise NotImplementedError("Implement in subclass")

    def __getitem__(self, key):
        return self.at(key)


class WholeImageData(ImageData):

    def __init__(self, manifest, img):
        super().__init__(manifest)
        self._img = img
        self._pa = img.load()

    @staticmethod
    def create(manifest, filepath):
        img = Image.open(filepath)
        return WholeImageData(manifest, img)

    def time_taken(self):
        dt_str = self._img._getexif()[DATETIME_EXIF]
        dt_obj = datetime.strptime(dt_str, DATETIME_FMT)
        return dt_obj

    def register(self, heatmap, coord):
        heatmap.add(coord)

    @staticmethod
    def coordinates(manifest, dim):
        xs, ys = range(dim[0]), range(dim[1])
        return set(itertools.product(xs, ys))

    def at(self, coord):
        return self._pa[coord]


class ChunkImageData(ImageData):

    @staticmethod
    def create(manifest, filepath):
        chunk_obj = PixelChunk.of(filepath)
        return ChunkImageData(manifest, chunk_obj)

    def __init__(self, manifest, chunk_obj):
        super().__init__(manifest)
        self._chunk_obj = chunk_obj
        self._chunks = chunk_obj.rgb_chunks()

    def _chunk_dim(self):
        return self.manifest.chunk_dimensions()

    def time_taken(self):
        dt_str = self._chunk_obj.file_datetime()
        dt = datetime.strptime(dt_str, DATETIME_FMT)
        return dt

    def register(self, heatmap, coord):
        chunk_width, chunk_height = self._chunk_dim()
        x, y = coord
        for deltax in range(chunk_width):
            for deltay in range(chunk_height):
                pos = x + deltax, y + deltay
                heatmap.add(pos)

    @staticmethod
    def coordinates(manifest, dim):
        chunk_width, chunk_height = manifest.chunk_dimensions()
        xs = range(0, dim[0], chunk_width)
        ys = range(0, dim[1], chunk_height)
        return set(itertools.product(xs, ys))

    def at(self, coord):
        return self._chunks[coord]


###############################################################################
# Utilities                                                                   #
###############################################################################

def parse_datetime(s):
    return datetime.strptime(s, DATETIME_FMT)


def unparse_datetime(dt):
    return dt.strftime(DATETIME_FMT)
