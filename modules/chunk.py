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
FILE_DATETIME = 'file-datetime'
CHUNK = 'chunks'
COORDINATES = 'coordinates'
RGB_AVERAGE = 'rgb'
RGB_VARIANCE = 'variance'

#pillow
DATETIME_EXIF = 36867


#Class
class PixelChunk(object):

    def __init__(self, image_filepath):
        super(PixelChunk, self).__init__()
        self.image_file_name = image_filepath
        self.image = Image.of(image_filepath)
        self.json_data = {}
        self.add_image_data()

    def add_chunk(self, coordinate):
        total_chunk_coordinates = total_chunk_coordinates(coordinate)
        color_average, color_variance = color_values(self.image, total_chunk_coordinates)
        self.json_data[CHUNK].append({
            COORDINATES: coordinate
            RGB_AVERAGE: color_average
            RGB_VARIANCE: color_variance
        })

    def add_image_data(self):
        self.json_data[FILE_DATETIME] = time_taken(self.image)

    def write(self):
        json_file = self.image_file_name.replace('.jpg', '.txt')
        with open(json_file, 'w') as outfile:
            json.dump(json_data, outfile)


#Helpers
def color_values(image, coordinates):
    average_red, average_green, average_blue = average_rgb_values(image, cordinates)
    average_rgb = rgb_luminosity_average(image, average_red, average_green, average_blue)
    average_variance = rgb_variance(image, coordinates, average_red, average_green, average_blue)
    return average_rgb, average_variance

def average_rgb_values(image, coordinates):
    average_red = 0
    average_green = 0
    average_blue = 0
    for point in coordinates:
        rgb = image.getpixel(point)
        average_red = average_red + rgb[RED_INDEX]
        average_green = average_green + rgb[GREEN_INDEX]
        average_blue = average_blue + rgb[BLUE_INDEX]
    average_red = average_red / len(coordinates)
    average_green = average_green / len(coordinates)
    average_blue = average_blue / len(coordinates)
    return average_red, average_green, average_blue

#Why use this algorithm over a normal average
#https://bit.ly/2E8XGPn
def rgb_luminosity_average(image, coordinate, average_red, average_green, average_blue):
    red_value = average_red * LUMINOSITY_RED_VALUE
    green_value = average_green * LUMINOSITY_GREEN_VALUE
    blue_value = average_blue * LUMINOSITY_BLUE_VALUE
    return red_value + green_value + blue_value

#why using a classic rgb average instead of luminosity
#https://bit.ly/2E8XGPn (same link as rbg lumonisty)
def rgb_variance(image, coordinates, average_red, average_green, average_blue):
    var_red, var_green, var_blue = rgb_variance_values(image, coordinates
                            average_red, average_green, average_blue)
    variance = (1.0/3.0) * (var_red + var_green + var_blue)
    return variance + rgb_variance_rough_covariance_term(average_red, average_green, average_blue)

def rgb_variance_values(image, coordinates, average_red, average_green, average_blue):
    var_red = 0
    var_green = 0
    var_blue =  0
    for point in coordinates:
        rgb = image.getpixel(point)
        var_red = (average_red - rgb[RED_INDEX]) ** 2
        var_green = (average_green - rgb[GREEN_INDEX]) ** 2
        var_blue = (average_blue - rgb[BLUE_INDEX]) ** 2
    var_red = var_red / len(scoordinates)
    var_green = var_green / len(coordinates)
    var_blue = var_blue / len(coordinates)
    return var_red, var_green, var_blue

def rgb_variance_rough_covariance_term(average_red, average_green, average_blue):
    value_one = (2.0/9.0) * ((average_red**2) + (average_green**2) +
                    (average_blue**2))
    value_two = ((average_red*average_green) + (average_red*average_blue) +
                (average_blue*average_green)) * (2.0/9.0)
    return value_one - value_two

def total_chunk_coordinates(self, coordinate):
    x = coordinate[0]
    x_end = x + DEFAULT_CHUNK_WIDTH
    y = coordinate[1]
    y_end = y + DEFAULT_CHUNK_HEIGHT
    xs, ys = range(x, x_end), range(y, y_end)
    return set(itertools.product(xs, ys))

def time_taken(img):
    dt_str = img._getexif()[DATETIME_EXIF]
    dt_obj = datetime.strptime(dt_str, DATETIME_FMT)
    return dt_obj

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

def create_chunks(image_filepath, manifest):
    chunk_json = PixelChunk(image_filepath)

    dimensions = manifest.dimensions()
    all_coordinates = coordinates(dimensions)
    for coordinate in all_coordinates[::DEFAULT_CHUNK_WIDTH]
        chunk_json.add_chunk(coordinate)
    chunk_json.write()

def coordinates(dim):
    xs, ys = range(dim[0]), range(dim[1])
    return set(itertools.product(xs, ys))

if __name__ == '__main__':
    main()
