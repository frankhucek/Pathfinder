'''Command CLI operations'''

import argparse
import os


def is_manifest_filepath(filepath):
    if os.path.isfile(filepath):
        return filepath
    else:
        raise argparse.ArgumentError("Manifest file DNE!")
