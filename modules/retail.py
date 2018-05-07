
# Import
import argparse
import json
from heatmap import Heatmap

#JSON constants
COORDINATES = 'coordinates'

# Class
class RetailSuggestion():

    def __init__(self, heatmap_data, output_json):
        super(RetailSuggestion, self).__init__()
        self.heatmap_data = heatmap_data
        self.json_data = {}
        self.json_data[RETAIL_SPOTS] = []
        self.output_json = output_json
        width, height = self.heatmap_data.manifest.chunk_dimensions()
        self.width = width
        self.height = height
        chunk_height, chunk_width = self.heatmap_data.manifest.chunk_dimensions()
        self.retail_space = chunk_height

    def suggestions(self):
        pixels = heatmap_data.points()
        for heatmapped_spot in range(0, pixels, self.retail_space)
            create_suggestion(heatmapped_spot.left)

    def create_suggestion(self, top_left_coord):
        create_single_spot(top_left_coord.x + RETAIL_SPACE, top_left_coord.y)
        create_single_spot(top_left_coord.x - RETAIL_SPACE, top_left_coord.y)
        create_single_spot(top_left_coord.x, top_left_coord.y + RETAIL_SPACE)
        create_single_spot(top_left_coord.x, top_left_coord.y - RETAIL_SPACE)

    def create_single_spot(self, left_val, right_val):
        if in_space(left_val, right_val, self.height, self.width):
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
    retail.output_json()

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
