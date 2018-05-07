'''chunk module

Provides tools with which to convert a raw image to a text file
containing chunked data.

Each chunk holds the position, average RGB value, and variance
of that chunk of the image.
'''

# Imports
import json
import argparse
import itertools
from PIL import Image

# Constants
# Chosen arbitrarly, can test different chunk sizes and determine which is best
DEFAULT_CHUNK_WIDTH = 36
DEFAULT_CHUNK_HEIGHT = 36

# Values for analyzing RGB values
RED_INDEX = 0
GREEN_INDEX = 1
BLUE_INDEX = 2
LUMINOSITY_RED_VALUE = .299
LUMINOSITY_GREEN_VALUE = .587
LUMINOSITY_BLUE_VALUE = .114

# JSON dict
FILE_DATETIME = 'file-datetime'
HEIGHT = 'height'
WIDTH = 'width'
CHUNK = 'chunks'
COORDINATES = 'coordinates'
RGB_AVERAGE = 'rgb'
RGB_VARIANCE = 'variance'

# pillow
DATETIME_EXIF = 36867
DIM_WIDTH = 256
DIM_HEIGHT = 257


# Class
class PixelChunk(object):

    @staticmethod
    def new(image_filepath, chunk_width, chunk_height):
        image = Image.open(image_filepath)
        output_json = image_filepath.replace('.jpg', '.txt')
        exif_date = image._getexif()
        width = exif_date[DIM_WIDTH]
        height = exif_date[DIM_HEIGHT]
        file_date = exif_date[DATETIME_EXIF]
        return PixelChunk(image.load(), output_json, width, height,
                          chunk_width, chunk_height, file_date)

    @staticmethod
    def of(filepath, chunk_width, chunk_height):
        with open(filepath) as f:
            chunk_json = json.load(f)
        file_date = chunk_json[FILE_DATETIME]
        width = chunk_json[WIDTH]
        height = chunk_json[HEIGHT]
        image = filepath
        output_json = filepath
        chunks = chunk_json[CHUNK]
        return PixelChunk(image, output_json,
                          width, height,
                          chunk_width, chunk_height,
                          file_date,
                          chunks)

    def __init__(self, image, output_json,
                 width, height, chunk_width, chunk_height,
                 file_date, chunks=None):
        super(PixelChunk, self).__init__()
        self.image = image
        self.output_json = output_json
        self.width = width
        self.height = height
        self.chunk_width = chunk_width
        self.chunk_height = chunk_height
        self.json_data = {}
        self.json_data[FILE_DATETIME] = file_date
        self.json_data[WIDTH] = width
        self.json_data[HEIGHT] = height
        self.json_data[CHUNK] = chunks if chunks else []

    def add_chunk(self, coordinate):
        total_coordinates = total_chunk_coordinates(coordinate,
                                                    self.chunk_width,
                                                    self.chunk_height)
        color_average, color_variance = color_values(self.image, total_coordinates)
        self.json_data[CHUNK].append({
            COORDINATES: coordinate,
            RGB_AVERAGE: color_average,
            RGB_VARIANCE: color_variance
        })

    def file_datetime(self):
        return self.json_data[FILE_DATETIME]

    def rgb_chunks(self):
        chunks = {}
        for chunk in self.json_data[CHUNK]:
            coord = tuple(chunk[COORDINATES])
            chunks[coord] = chunk[RGB_AVERAGE]
        return chunks

    def write(self, new_filepath):
        with open(new_filepath, 'w') as outfile:
            json.dump(self.json_data, outfile)

    def dimensions(self):
        return self.width, self.height


# Helpers
def color_values(image, coordinates):
    average_red, average_green, average_blue = average_rgb_values(image, coordinates)
    average_rgb = rgb_luminosity_average(image, average_red, average_green, average_blue)
    average_variance = rgb_variance(image, coordinates, average_red, average_green, average_blue)
    return average_rgb, average_variance


def average_rgb_values(image, coordinates):
    average_red = 0
    average_green = 0
    average_blue = 0
    for point in coordinates:
        rgb = image[point]
        average_red = average_red + rgb[RED_INDEX]
        average_green = average_green + rgb[GREEN_INDEX]
        average_blue = average_blue + rgb[BLUE_INDEX]
    average_red = average_red / len(coordinates)
    average_green = average_green / len(coordinates)
    average_blue = average_blue / len(coordinates)
    return average_red, average_green, average_blue


# Why use this algorithm over a normal average
# https://bit.ly/2E8XGPn
def rgb_luminosity_average(image, average_red, average_green, average_blue):
    red_value = average_red * LUMINOSITY_RED_VALUE
    green_value = average_green * LUMINOSITY_GREEN_VALUE
    blue_value = average_blue * LUMINOSITY_BLUE_VALUE
    return red_value + green_value + blue_value


# why using a classic rgb average instead of luminosity
# https://bit.ly/2E8XGPn (same link as rbg lumonisty)
def rgb_variance(image, coordinates, average_red, average_green, average_blue):
    var_red, var_green, var_blue = rgb_variance_values(image,
                                                       coordinates,
                                                       average_red,
                                                       average_green,
                                                       average_blue)
    variance = (1.0 / 3.0) * (var_red + var_green + var_blue)
    return variance + rgb_variance_rough_covariance_term(average_red,
                                                         average_green,
                                                         average_blue)


def rgb_variance_values(image, coordinates, average_red, average_green, average_blue):
    var_red = 0
    var_green = 0
    var_blue = 0
    for point in coordinates:
        rgb = image[point]
        var_red = (average_red - rgb[RED_INDEX]) ** 2
        var_green = (average_green - rgb[GREEN_INDEX]) ** 2
        var_blue = (average_blue - rgb[BLUE_INDEX]) ** 2
    var_red = var_red / len(coordinates)
    var_green = var_green / len(coordinates)
    var_blue = var_blue / len(coordinates)
    return var_red, var_green, var_blue


def rgb_variance_rough_covariance_term(average_red, average_green, average_blue):
    value_one = (2.0 / 9.0) * ((average_red**2) + (average_green**2) +
                               (average_blue**2))
    value_two = ((average_red * average_green) + (average_red * average_blue) +
                 (average_blue * average_green)) * (2.0 / 9.0)
    return value_one - value_two


def total_chunk_coordinates(coordinate,
                            chunk_width,
                            chunk_height):
    x = coordinate[0]
    x_end = x + chunk_width
    y = coordinate[1]
    y_end = y + chunk_height
    xs, ys = range(x, x_end), range(y, y_end)
    return set(itertools.product(xs, ys))


# Main functions
def main():
    args = get_args()
    if args.op == "create_chunks":
        create_chunks(args.image_filepath, DEFAULT_CHUNK_WIDTH, DEFAULT_CHUNK_HEIGHT)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=["create_chunks"])
    parser.add_argument("image_filepath",
                        help="Image files")
    return parser.parse_args()


def create_chunks(image_filepath, new_filepath, chunk_width, chunk_height):
    chunk_json = PixelChunk.new(image_filepath, chunk_width, chunk_height)

    dimensions = chunk_json.dimensions()
    all_coordinates = coordinates(dimensions,
                                  chunk_width,
                                  chunk_height)
    for coordinate in all_coordinates:
        chunk_json.add_chunk(coordinate)
    chunk_json.write(new_filepath)


def coordinates(dim,
                chunk_width,
                chunk_height):
    xs, ys = range(0, dim[0], chunk_width), range(0, dim[1], chunk_height)
    return set(itertools.product(xs, ys))


if __name__ == '__main__':
    main()
