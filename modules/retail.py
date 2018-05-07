
# Import
import argparse
import json
from heatmap import Heatmap

#JSON constants
COORDINATES = 'coordinates'
RETAIL_SPOTS = 'retail'

# Class
class RetailSuggestion():

    def __init__(self, heatmap_data, output_json, hotdog_limit):
        super(RetailSuggestion, self).__init__()
        self.heatmap_data = heatmap_data
        self.json_data = {}
        self.json_data[RETAIL_SPOTS] = []
        self.output_file = output_json
        width, height = self.heatmap_data.size
        self.width = width
        self.height = height
        self.hotdog_limit = hotdog_limit
        chunk_height, chunk_width = self.heatmap_data.manifest.chunk_dimensions()
        self.retail_space = chunk_height

    def suggestions(self):
        hm_points = self.heatmap_data.points()
        coord_range = self.heatmap_data.field
        for x in range(0, self.width, self.retail_space):
            for y in range(0, self.height, self.retail_space):
                if hm_points[y][x] > self.hotdog_limit:
                    self.create_suggestion(x, y)

    def create_suggestion(self, x, y):
        self.create_single_spot(x + self.retail_space, y)
        self.create_single_spot(x - self.retail_space, y)
        self.create_single_spot(x, y + self.retail_space)
        self.create_single_spot(x, y - self.retail_space)

    def create_single_spot(self, left_val, right_val):
        if in_space(left_val, right_val, self.height, self.width):
            coordinates = left_val, right_val
            self.json_data[RETAIL_SPOTS].append({
                COORDINATES: coordinates
            })

    def write_json(self, new_filepath):
        with open(new_filepath, 'w') as outfile:
            json.dump(self.json_data, outfile)

# Helpers
def create_retail(heatmap_filepath, new_filepath, hotdog_limit):
    hm = Heatmap.load(heatmap_filepath)
    output_json = heatmap_filepath.replace('.heatmap', 'retail.json')
    retail = RetailSuggestion(hm, output_json, hotdog_limit)
    retail.suggestions()
    retail.write_json(new_filepath)

def in_space(x, y, height, width):
    if x < 0 or y < 0:
        return False
    if x >= width or y >= height:
        return False
    return True

# Main
def main():
    args = get_args()
    if args.op == "create_retail":
        create_retail(args.image_filepath, args.out_filepath, args.hotdog_limit)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("op",
                        choices=["create_retail"])
    parser.add_argument("image_filepath",
                        help="Image files")
    parser.add_argument("out_filepath",
                        help="A filepath to write to")
    parser.add_argument("hotdog_limit",
                        type=float,
                        help="normalized to 1 the minimum value to put retail spots near")
    return parser.parse_args()

if __name__ == '__main__':
    main()
