# Imports
import json
import cli
from PIL import Image


# Constants
#Chosen arbitrarly, can test different chunk sizes and determine which is best
DEFAULT_CHUNK_WIDTH = 36
DEFAULT_CHUNK_HEIGHT = 36

#Values for analyzing RGB values
RED_INDEX = 0
GREEN_INDEX = 0
BLUE_INDEX = 0
LUMINOSITY_RED_VALUE = .299
LUMINOSITY_GREEN_VALUE = .587
LUMINOSITY_BLUE_VALUE =  .114

#JSON dict
CHUNK = 'chunks'
COORDINATES = 'coordinates'
RGB_AVERAGE = 'rgb'
RGB_VARIANCE = 'variance'


#Class
class PixelChunk(object):

    def __init__(self, image_name, image):
        super(PixelChunk, self).__init__()
        self.image_file_name = image_name
        self.image = image
        self.json_data = {}

    def add_chunk(self, coordinate):
        color_average, color_variance = color_values(self.image, coordinate)
        self.json_data[CHUNK].append({
            COORDINATES: coordinate
            RGB_AVERAGE: color_average
            RGB_VARIANCE: color_variance
        })

    def write(self):
        json_file = self.image_name + '.txt'
        with open(json_file, 'w') as outfile:
            json.dump(json_data, outfile)


#Helpers
def create_chunks(image_filepath, manifest):
    chunk_json = PixelChunk(image_filepath, image, width, height)

    dimensions = manifest.dimensions()
    all_coordinates = coordinates(dimensions)
    for coordinate in all_coordinates[::DEFAULT_CHUNK_WIDTH]
        chunk_json.add_chunk(coordinate)
    chunk_json.write()


def coordinates(dim):
    xs, ys = range(dim[0]), range(dim[1])
    return set(itertools.product(xs, ys))


def color_values(image, coordinate):
    average_values = average_rgb_values(image)
    average = rgb_luminosity_average(image, coordinate)

#Why use this algorithm over a normal average
#https://bit.ly/2E8XGPn
def rgb_luminosity_average(image):
    average_red, average_green, average_blue = self.average_rgb_values(image)
    red_value = average_red * LUMINOSITY_RED_VALUE
    green_value = average_green * LUMINOSITY_GREEN_VALUE
    blue_value = average_blue * LUMINOSITY_BLUE_VALUE
    return red_value + green_value + blue_value

def average_rgb_values(image):
    average_red = 0
    average_green = 0
    average_blue = 0
    for point in self.points:
        rgb = image.getpixel(point)
        average_red = average_red + rgb[RED_INDEX]
        average_green = average_green + rgb[GREEN_INDEX]
        average_blue = average_blue + rgb[BLUE_INDEX]
    average_red = average_red / len(self.points)
    average_green = average_green / len(self.points)
    average_blue = average_blue / len(self.points)
    return average_red, average_green, average_blue

#why using a classic rgb average instead of luminosity
#https://bit.ly/2E8XGPn (same link as rbg lumonisty)
def rgb_variance(image):
    #+ (1/3)⋅(VarRed + VarGreen + VarBlue)
    var_red, var_green, var_blue = self.rgb_variance_values(image)
    variance = (1.0/3.0) * (var_red + var_green + var_blue)
    return variance + self.rgb_variance_rough_covariance_term()

def rgb_variance_values(image):
    average_red, average_green, average_blue = self.average_rgb_values()
    var_red = 0
    var_green = 0
    var_blue =  0
    for point in self.points:
        rgb = image.getpixel(point)
        var_red = (average_red - rgb[RED_INDEX]) ** 2
        var_green = (average_green - rgb[GREEN_INDEX]) ** 2
        var_blue = (average_blue - rgb[BLUE_INDEX]) ** 2
    var_red = var_red / len(self.points)
    var_green = var_green / len(self.points)
    var_blue = var_blue / len(self.points)
    return var_red, var_green, var_blue

def rgb_variance_rough_covariance_term(average_rgb_values):
    average_red, average_green, average_blue = average_rgb_values
    value_one = (2.0/9.0) * ((average_red**2) + (average_green**2) +
                    (average_blue**2))
    value_two = ((average_red*average_green) + (average_red*average_blue) +
                (average_blue*average_green)) * (2.0/9.0)
    return value_one - value_two


#Main functions
def main():
    args = get_args()
    manifest = Manifest.from_filepath(args.manifest)
    if args.op == "create_chunks":
        create_chunks(args.image, manifest)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=["create_chunks"])
    parser.add_argument("image",
                        nargs="+",
                        help="Image files")
    parser.add_argument("manifest",
                        help="manifest filepath",
                        type=cli.is_manifest_filepath)
    return parser.parse_args()

if __name__ == '__main__':
    main()
