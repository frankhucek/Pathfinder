
# Import
import argparse
from heatmap import Heatmap

# Class
class RetailSuggestion():

    def __init__(self, heatmap_data):
        super(RetailSuggestion, self).__init__()
        self.heatmap_data = heatmap_data

    def suggestions(self):
        pass

# Helpers
def create_retail(heatmap):
    hm = Heatmap.load(heatmap_filepath)
    retail = RetailSuggestion(hm)
    retail.suggestions()

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
