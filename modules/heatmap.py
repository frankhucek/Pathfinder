#! /usr/bin/env python3

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import itertools
import os
import json
import pickle

from datetime import datetime

import numpy as np
from PIL import Image

from chunk import PixelChunk
from manifest import Manifest
from mapping import Geometry
import mapping
import cli


###############################################################################
# Constants                                                                   #
###############################################################################

DEFAULT_WINDOW_SIZE = 2
DEFAULT_COLOR_THRESH = 50

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


class TimePeriod(object):

    def __init__(self, start, end):
        super(TimePeriod, self).__init__()
        self.start = start
        self.end = end

    def contains(self, dt):
        return self.start <= dt and dt <= self.end


class CoordRange(object):

    def __init__(self, image_corners):
        self._min_x = min(x for x, y in image_corners)
        self._max_x = max(x for x, y in image_corners)
        self._min_y = min(x for x, y in image_corners)
        self._max_y = max(x for x, y in image_corners)

    def contains(self, coord):
        x, y = coord
        return self._min_x < x and x < self._max_x and \
            self._min_y < y and y < self._max_y

    def coordinates(self):
        for x in range(self._min_x, self._max_x + 1):
            for y in range(self._min_y, self._max_y + 1):
                yield (x, y)


class Heatmap(object):

    @staticmethod
    def new(manifest):
        width, height = manifest.dimensions()
        points = np.zeros((height, width))
        return Heatmap(manifest, points)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def __init__(self, manifest, points):
        super(Heatmap, self).__init__()
        self.manifest = manifest
        self.size = manifest.dimensions()
        self.geom = Geometry.from_manifest(manifest)
        self.field = CoordRange(manifest.image_corners())
        self.count = 0
        self._points = points

    def add(self, coord):
        self.count += 1
        self.set(coord, self.at(coord) + 1)

    def set(self, coord, val):
        self._points[self._flip(coord)] = val

    def at(self, coord):
        return self._points[self._flip(coord)]

    def _flip(self, coord):
        x, y = coord
        return y, x

    def record(self,
               img_files,
               period,
               window_size=DEFAULT_WINDOW_SIZE,
               color_thresh=DEFAULT_COLOR_THRESH):
        data_type = ImageData.sub_type(img_files)

        images = image_obj_sequence(self.manifest,
                                    img_files,
                                    period)

        image_sets = windows(images, window_size)

        for idx, image_set in enumerate(image_sets):

            print("image_set: {}".format(idx))

            all_coordinates = data_type.coordinates(self.manifest,
                                                    self.size)
            for coord in all_coordinates:

                if is_movement(image_set, coord, color_thresh):
                    image_set[0].register(self, coord)

    def points(self):
        return self._points / np.max(self._points)

    def project_point(self, coord, scale):
        raw = mapping.image_to_blueprint(coord,
                                         self.geom,
                                         self.size)

        projected = tuple(int(round(x * scale)) for x in raw)
        return projected

    def project(self, filepath, desired_width):

        image_corners = self.manifest.image_corners()
        lower_right = image_corners[3]
        b_x, b_y = self.project_point(lower_right, 1)

        scale = desired_width / b_x
        new_size = (int(b_y * scale), int(b_x * scale))
        blueprint_values = np.zeros(new_size)

        def valid_coord(coord, shape):
            return all(c >= 0 and c < s
                       for c, s in zip(coord, shape))

        for x, y in self.field.coordinates():

            val = self.at((x, y))

            p_x, p_y = self.project_point((x, y), scale)

            if valid_coord((p_y, p_x), blueprint_values.shape):
                blueprint_values[p_y, p_x] += val

        normalized = blueprint_values / np.max(blueprint_values)
        self.write_bw_binary(normalized, filepath)

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    def write(self, filepath):
        self.write_bw_binary(self.points(), filepath)

    @staticmethod
    def write_bw_binary(arr, filepath):
        write_points = arr * 255
        uint_points = write_points.astype('uint8')
        im = Image.fromarray(uint_points, 'L')
        im.save(filepath)

    def __str__(self):
        attrs = [self.size[0],
                 self.size[1],
                 self.count]
        attr_str = "\n".join(str(x) for x in attrs)
        points = json.dumps(self.points(),
                            default=lambda x: list(x))
        string = "{}\n{}".format(attr_str, points)
        return string


###############################################################################
# Heatmap Tools                                                               #
###############################################################################

def new_heatmap(heatmap_filepath, manifest):
    hm = Heatmap.new(manifest)
    hm.save(heatmap_filepath)


def record_heatmap(heatmap_filepath,
                   img_files,
                   period,
                   window_size=DEFAULT_WINDOW_SIZE,
                   color_thresh=DEFAULT_COLOR_THRESH):
    hm = Heatmap.load(heatmap_filepath)
    hm.record(img_files,
              period,
              window_size,
              color_thresh)
    hm.save(heatmap_filepath)


def view_heatmap(heatmap_filepath,
                 output_filepath):
    hm = Heatmap.load(heatmap_filepath)
    hm.write(output_filepath)


def project_heatmap(heatmap_filepath,
                    project_filepath):
    hm = Heatmap.load(heatmap_filepath)
    hm.project(project_filepath)


###############################################################################
# Helpers                                                                     #
###############################################################################

def image_obj_sequence(manifest, img_files, period):
    images = [ImageData.create(manifest, fp)
              for fp in img_files]
    images = trim_by_date(images, period)
    images = sort_by_date(images)
    return images


def trim_by_date(images, period):
    return [x for x in images
            if period.contains(x.time_taken())]


def sort_by_date(images):
    return sorted(images, key=lambda x: x.time_taken())


def windows(images, window_size):
    chunks = []
    for start in range(len(images) - window_size):
        end = start + window_size
        chunk = images[start:end]
        chunks.append(chunk)
    return chunks


def extract_color_set(images, coord):
    return np.array([img[coord] for img in images])


def is_movement(images, coord,
                color_thresh=DEFAULT_COLOR_THRESH):
    '''determine if there is movement at a coordinate'''

    color_set = extract_color_set(images, coord)

    spread = np.ptp(color_set)
    return spread > color_thresh


###############################################################################
# Command line                                                                #
###############################################################################

def parse_time(s):
    try:
        return datetime.strptime(s, DATETIME_FMT)
    except ValueError:
        msg = "Illegal time format -- use {}".format(DATETIME_FMT)
        raise argparse.ArgumentTypeError(msg)


class MakeTimePeriodAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        time_period = TimePeriod(*values)
        setattr(namespace, self.dest, time_period)


def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="op")

    new_parser = subparsers.add_parser("new_heatmap",
                                       help="make new heatmap")
    new_parser.add_argument("heatmap_filepath",
                            help="file to contain heatmap")
    new_parser.add_argument("manifest",
                            type=cli.is_manifest_filepath,
                            help="file containing manifest")

    record_parser = subparsers.add_parser("record_heatmap",
                                          help="record imgs on heatmap")
    record_parser.add_argument("heatmap_filepath",
                               help="file containing heatmap")
    record_parser.add_argument("period",
                               help="time period to trim images",
                               nargs=2,
                               type=parse_time,
                               action=MakeTimePeriodAction)
    record_parser.add_argument("window_size",
                               help="size of sliding window",
                               type=int)
    record_parser.add_argument("color_thresh",
                               help="RGB magnitude of color difference",
                               type=int)
    record_parser.add_argument("images",
                               nargs="+",
                               help="Image files")

    view_heatmap = subparsers.add_parser("view_heatmap",
                                         help="see heatmap img")
    view_heatmap.add_argument("heatmap_filepath",
                              help="file containing heatmap")
    view_heatmap.add_argument("output_filepath",
                              help="file to contain heatmap img")

    project_parser = subparsers.add_parser("project_heatmap",
                                           help="project heatmap")
    project_parser.add_argument("heatmap_filename",
                                help="filename of heatmap")
    project_parser.add_argument("project_filename",
                                help="filename to project")
    project_parser.add_argument("desired_width",
                                type=int,
                                help="intended projection pixed width")

    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():

    args = get_args()

    if args.op == "new_heatmap":
        new_heatmap(args.heatmap_filepath,
                    Manifest.from_filepath(args.manifest))

    elif args.op == "record_heatmap":
        record_heatmap(args.heatmap_filepath,
                       args.images,
                       args.period,
                       args.window_size,
                       args.color_thresh)

    elif args.op == "view_heatmap":
        view_heatmap(args.heatmap_filepath,
                     args.output_filepath)

    elif args.op == "project_heatmap":
        heatmap = Heatmap.load(args.heatmap_filename)
        heatmap.project(args.project_filename,
                        args.desired_width)


if __name__ == '__main__':
    main()
