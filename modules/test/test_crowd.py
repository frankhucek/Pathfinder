
import sys
from pathlib import Path
cur_dir = Path(__file__).parents[0]
parent_dir = Path(__file__).parents[1]
if parent_dir not in sys.path:
    sys.path.insert(0, str(parent_dir))
if cur_dir not in sys.path:
    sys.path.insert(0, str(cur_dir))


###############################################################################
# Imports                                                                     #
###############################################################################

import pytest


###############################################################################
# Unit under test                                                             #
###############################################################################

import crowd
from crowd import FrequencyUnits


###############################################################################
# Constants                                                                   #
###############################################################################



###############################################################################
# Fixtures                                                                    #
###############################################################################



###############################################################################
# Test cases                                                                  #
###############################################################################

def test_frequency_units_of_nominal():
    s = "minutes"
    minutes = FrequencyUnits.of(s)
    assert isinstance(minutes, FrequencyUnits)


def test_frequency_units_of_nominal_case():
    s = "MINUTES"
    minutes = FrequencyUnits.of(s)
    assert isinstance(minutes, FrequencyUnits)


def test_frequency_units_of_failure():
    s = "giraffe"
    with pytest.raises(ValueError):
        FrequencyUnits.of(s)


def test_frequency_units_convert_nominal():
    s = "minutes"
    units = FrequencyUnits.of(s)
    people_per_sec = 120
    people_per_min = FrequencyUnits.convert(people_per_sec, units)
    assert 2 == people_per_min
