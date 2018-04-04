# Imports
import json
import cli
import argparse
import itertools
import json
from datetime import datetime
from PIL import Image

# Constants
#Chosen arbitrarly, can test different chunk sizes and determine which is best
DEFAULT_CHUNK_WIDTH = 36
DEFAULT_CHUNK_HEIGHT = 36

#Values for analyzing RGB values
RED_INDEX = 0
GREEN_INDEX = 1
BLUE_INDEX = 2
LUMINOSITY_RED_VALUE = .299
LUMINOSITY_GREEN_VALUE = .587
LUMINOSITY_BLUE_VALUE =  .114

#JSON dict
FILE_DATETIME = 'file-datetime'
HEIGHT = 'height'
WIDTH = 'width'
CHUNK = 'chunks'
COORDINATES = 'coordinates'
RGB_AVERAGE = 'rgb'
RGB_VARIANCE = 'variance'

#pillow
DATETIME_EXIF = 36867
DIM_WIDTH = 256
DIM_HEIGHT = 257


#Class
class PixelChunk(object):

    @staticmethod
    def new(image_filepath):
        image = Image.open(image_filepath)
        output_json = image_filepath.replace('.jpg', '.txt')
        exif_date = image._getexif()
        width = exif_date[DIM_WIDTH]
        height = exif_date[DIM_HEIGHT]
        file_date = exif_date[DATETIME_EXIF]
        return PixelChunk(image.load(), output_json, width, height, file_date)

    def __init__(self, image, output_json, width, height, file_date):
        super(PixelChunk, self).__init__()
        self.image = image
        self.output_json = output_json
        self.width = width
        self.height = height
        self.json_data = {}
        self.json_data[FILE_DATETIME] = file_date
        self.json_data[WIDTH] = width
        self.json_data[HEIGHT] = height
        self.json_data[CHUNK] = []

    def add_chunk(self, coordinate):
        total_coordinates = total_chunk_coordinates(coordinate)
        color_average, color_variance = color_values(self.image, total_coordinates)
        self.json_data[CHUNK].append({
            COORDINATES: coordinate,
            RGB_AVERAGE: color_average,
            RGB_VARIANCE: color_variance
        })

    def write(self):
        with open(self.output_json, 'w') as outfile:
            json.dump(self.json_data, outfile)

    def dimensions(self):
        return self.width, self.height


#Helpers
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

#Why use this algorithm over a normal average
#https://bit.ly/2E8XGPn
def rgb_luminosity_average(image, average_red, average_green, average_blue):
    red_value = average_red * LUMINOSITY_RED_VALUE
    green_value = average_green * LUMINOSITY_GREEN_VALUE
    blue_value = average_blue * LUMINOSITY_BLUE_VALUE
    return red_value + green_value + blue_value

#why using a classic rgb average instead of luminosity
#https://bit.ly/2E8XGPn (same link as rbg lumonisty)
def rgb_variance(image, coordinates, average_red, average_green, average_blue):
    var_red, var_green, var_blue = rgb_variance_values(image, coordinates,
                                average_red, average_green, average_blue)
    variance = (1.0/3.0) * (var_red + var_green + var_blue)
    return variance + rgb_variance_rough_covariance_term(average_red, average_green, average_blue)

def rgb_variance_values(image, coordinates, average_red, average_green, average_blue):
    var_red = 0
    var_green = 0
    var_blue =  0
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
    value_one = (2.0/9.0) * ((average_red**2) + (average_green**2) +
                    (average_blue**2))
    value_two = ((average_red*average_green) + (average_red*average_blue) +
                (average_blue*average_green)) * (2.0/9.0)
    return value_one - value_two

def total_chunk_coordinates(coordinate):
    x = coordinate[0]
    x_end = x + DEFAULT_CHUNK_WIDTH
    y = coordinate[1]
    y_end = y + DEFAULT_CHUNK_HEIGHT
    xs, ys = range(x, x_end), range(y, y_end)
    return set(itertools.product(xs, ys))

#Main functions
def main():
    args = get_args()
    if args.op == "create_chunks":
        create_chunks(args.image_filepath)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=["create_chunks"])
    parser.add_argument("image_filepath",
                        help="Image files")
    return parser.parse_args()

def create_chunks(image_filepath):
    chunk_json = PixelChunk.new(image_filepath)

    dimensions = chunk_json.dimensions()
    all_coordinates = coordinates(dimensions)
    for coordinate in all_coordinates:
        chunk_json.add_chunk(coordinate)
    chunk_json.write()

def coordinates(dim, chunk_width=DEFAULT_CHUNK_WIDTH,
        chunk_height=DEFAULT_CHUNK_HEIGHT):
    xs, ys = range(0, dim[0], chunk_width), range(0, dim[1], chunk_height)
    return set(itertools.product(xs, ys))

if __name__ == '__main__':
    main()
