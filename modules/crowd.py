#!/usr/bin/env python3

###############################################################################
# Imports                                                                     #
###############################################################################

import argparse
import json

from heatmap import Heatmap, HeatmapSeries, TimePeriod
from enum import Enum


###############################################################################
# Constants                                                                   #
###############################################################################

CROWD_FACTOR = 0.00000940981


class FrequencyUnits(Enum):
    SECONDS = 1
    MINUTES = 60
    HOURS = 3600
    DAYS = 86400

    @staticmethod
    def convert(people_per_sec, unit):
        return people_per_sec / unit.value

    @classmethod
    def of(cls, s):
        key = s.upper()
        try:
            return cls[key]
        except KeyError:
            raise ValueError("Invalid frequency unit {}".format(key))

    def unit_name(self):
        return self.name.lower()[0:-1]

    @classmethod
    def choices(cls):
        return [e for e in cls]


###############################################################################
# API                                                                         #
###############################################################################

def write_total(heatmap_filepath,
                output_filepath):
    total = estimate_total(heatmap_filepath)
    with open(output_filepath, 'w') as f:
        dct = {"total": total}
        json.dump(dct, f, indent=3)


def write_frequency(series_heatmap_fp,
                    output_filepath,
                    units,
                    aggregate):
    with open(output_filepath, 'w') as f:
        intervals = estimate_frequency(series_heatmap_fp, units, aggregate)
        dct = dict_format(intervals, units)
        json.dump(dct, f, indent=3)


###############################################################################
# Helper functions                                                            #
###############################################################################

def estimate_total(heatmap_filepath):
    hm = Heatmap.load(heatmap_filepath)
    return estimate_total_hm(hm)


def estimate_frequency(series_heatmap_fp, units, aggregate):
    series = HeatmapSeries.load(series_heatmap_fp)
    heatmaps = series.subheatmaps()

    obj_per_sec = {}

    for heatmap in heatmaps:
        obj_per_sec[heatmap] = estimate_obj_per_sec(heatmap)

    # generate list of (time_period, total) tuples
    if aggregate:
        intervals = average_frequency(obj_per_sec)
    else:
        intervals = tabled_frequencies(obj_per_sec)

    converted_intervals = convert(intervals, units)

    return converted_intervals


def estimate_total_hm(hm):
    rate = estimate_obj_per_sec(hm)
    seconds = hm.period.duration().seconds
    total = rate * seconds
    return total


def estimate_obj_per_sec(hm):
    count = hm.count
    seconds = hm.period.duration().seconds
    count_per_sec = count / seconds if seconds else 0

    obj_per_sec = count_per_sec * CROWD_FACTOR

    return obj_per_sec


def average_frequency(obj_per_sec):
    total_period = None
    total_seconds = 0
    total_obj = 0
    for heatmap, rate in obj_per_sec.items():
        total_period = TimePeriod.union(heatmap.period, total_period)
        duration = heatmap.period.duration().seconds
        obj = duration * rate

        total_seconds += duration
        total_obj += obj

    frequency = total_obj / total_seconds if total_seconds else 0
    return [(total_period, frequency)]


def tabled_frequencies(obj_per_sec):
    table = []
    for heatmap, rate in obj_per_sec.items():
        table.append((heatmap.period, rate))
    return table


def str_format(intervals, units):
    units_line = ["Units: people per {}".format(units.unit_name())]
    strs = ["{}: {}".format(p, r) for p, r in intervals]
    lines = units_line + strs
    return "\n".join(lines)


def dict_format(intervals, units):
    dct = {
        "units": "people per {}".format(units.unit_name()),
        "data": [dict_of_entry(i) for i in intervals]
    }
    return dct


def dict_of_entry(entry):
    period, rate = entry
    return {"start": str(period.start),
            "end": str(period.end),
            "rate": rate}


def convert(intervals, units):
    converted = []
    for period, rate in intervals:
        conv_rate = FrequencyUnits.convert(rate, units)
        converted.append((period, conv_rate))
    return converted


###############################################################################
# CLI                                                                         #
###############################################################################

def valid_units(s):
    try:
        return FrequencyUnits.of(s)
    except ValueError:
        msg = "Could not convert '{}' to a frequency unit".format(s)
        raise argparse.ArgumentTypeError(msg)


def valid_aggregate(s):
    if s in ["true", "t"]:
        return True
    elif s in ["false", "f"]:
        return False
    else:
        msg = "Could not convert '{}' to an aggregate flag".format(s)
        raise argparse.ArgumentTypeError(msg)


def get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="op")

    total_parser = subparsers.add_parser("estimate_total",
                                         help="estimate crowd number")
    total_parser.add_argument("heatmap_filepath",
                              help="file containing heatmap")
    total_parser.add_argument("--write", "-w",
                              help="write or not")

    frequency_parser = subparsers.add_parser("estimate_frequency")
    frequency_parser.add_argument("series_filepath",
                                  help="heatmap series")
    frequency_parser.add_argument("units",
                                  type=valid_units,
                                  choices=FrequencyUnits.choices(),
                                  help="frequency units")
    frequency_parser.add_argument("aggregate",
                                  type=valid_aggregate,
                                  help="flag of whether to aggregate results")
    frequency_parser.add_argument("--write", "-w",
                                  help="write or not")

    return parser.parse_args()


###############################################################################
# Main script                                                                 #
###############################################################################

def main():
    args = get_args()

    if args.op == "estimate_total":
        if args.write:
            write_total(args.heatmap_filepath,
                        args.write)
        else:
            total = estimate_total(args.heatmap_filepath)
            print(total)

    elif args.op == "estimate_frequency":
        if args.write:
            write_frequency(args.series_filepath,
                            args.write,
                            args.units,
                            args.aggregate)
        else:
            intervals = estimate_frequency(args.series_filepath,
                                           args.units,
                                           args.aggregate)
            report = str_format(intervals, args.units)
            print(report)


if __name__ == '__main__':
    main()
