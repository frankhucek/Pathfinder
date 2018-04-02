
import os
import datetime

from PIL import Image

FMT = "%Y:%m:%d %H:%M:%S"


def get_date_taken(path):
    img = Image.open(path)
    dt_str = img._getexif()[36867]
    dt_obj = datetime.datetime.strptime(dt_str, FMT)
    return dt_obj


def main():
    datetimes = []

    for file in os.listdir("."):
        if file.endswith(".jpg"):
            datetimes.append(get_date_taken(file))

    datetimes = sorted(datetimes)

    print("\n".join(x.strftime(FMT) for x in datetimes))


if __name__ == '__main__':
    main()
