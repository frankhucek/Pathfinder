
# Import
import argparse
import json
from heatmap import Heatmap

#Probably should remove this from being hardcoded
#Right now should just use a constant value
RETAIL_SPACE = 36
WIDTH = 2592
HEIGHT = 1944
#JSON constants
COORDINATES = 'coordinates'

# Class
class RetailSuggestion():

    def __init__(self, heatmap_data, output_json):
        super(RetailSuggestion, self).__init__()
        self.heatmap_data = heatmap_data
        self.json_data = {}
        self.json_data[RETAIL_SPOTS] = []

    def suggestions(self):
        # get heatmapped areas
        for heatmapped_spot in mapped:
            #TODO:
            create_suggestion(heatmapped_spot.left)

    def create_suggestion(self, top_left_coord):
        create_single_spot(top_left_coord.x + RETAIL_SPACE, top_left_coord.y)
        create_single_spot(top_left_coord.x - RETAIL_SPACE, top_left_coord.y)
        create_single_spot(top_left_coord.x, top_left_coord.y + RETAIL_SPACE)
        create_single_spot(top_left_coord.x, top_left_coord.y - RETAIL_SPACE)

    def create_single_spot(self, left_val, right_val):
        if in_space(left_val, right_val, HEIGHT, WIDTH):
            coordinates = left_val, right_val
            self.json_data[RETAIL_SPOTS].append({
                COORDINATES: coordinates
            })

    def output_json(self):
        with open(self.output_json, 'w') as outfile:
            json.dump(self.json_data, outfile)

# Helpers
def create_retail(heatmap_filepath):
    hm = Heatmap.load(heatmap_filepath)
    output_json = image_filepath.replace('.jpg', 'retail.txt')
    retail = RetailSuggestion(hm, output_json)
    retail.suggestions()

def in_space(x, y, height, width):
    if x < 0 or y < 0 return False
    if x >= width or y >= height return False
    return True

# Main
def main():
    args = get_args()
    if args.op == "create_retail":
        create_retail(args.image_filepath)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=["create_retail"])
    parser.add_argument("image_filepath",
                        help="Image files")
    return parser.parse_args()

if __name__ == '__main__':
    main()
