# This is the python program for Pathfinder's Raspberry Pi
# image capture service.
# The details of this service are described in RPI_README.md

import time
import picamera
import os
import pathlib
import capture

JOB_ID = 0 # Different for each RPI unit
JOB_ROOT_DIR = "jobs"
resX = 1024 # default resolution values
resY = 768

def initialize_job_directory(job_root_dir, job_id):
    job_dir = job_root_dir + "/" + str(job_id)
    pathlib.Path(job_dir).mkdir(exist_ok=True) # makedir if doesnt exist
    return job_dir

def capture_series(resX, resY, num_photos, job_dir):
    i = 0
    while i < num_photos:
        print("Capturing photo " + str(i) + " into dir " + job_dir)
        capture.capture(resX, resY, i, job_dir)
        i+=1
    return

def main():
    job_dir = initialize_job_directory(JOB_ROOT_DIR, JOB_ID)
    capture_series(resX, resY, 4, job_dir)

main()
