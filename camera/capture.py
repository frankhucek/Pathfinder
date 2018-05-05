# This module provides the function capture()
# Provide capture with relevant parameters including
# resolution, photo_number, job directory, and job number, and it will take and save the
# photos to their specified locations

import time
import picamera
import client

CAPTURE_JOB_DIR = "job_captures/0"
DEFAULT_PHOTO_COUNT = 10

def capture(resolutionX, resolutionY, photo_number, job_directory):
    fname = ""
    with picamera.PiCamera() as camera:
        camera.resolution = (resolutionX,resolutionY)
        camera.start_preview()
        camera.rotation = 180
        # Camera init time slightly > 1 second
        time.sleep(2)
        filename = str(photo_number) + ".jpg"
        fname = filename
        camera.capture(job_directory + "/" + filename)
    return fname
# usage:
# capture(1024, 768, 0, "jobs/0")
# dir: job_captures/0

def capture_and_send_series(photo_count, job_dir):

    i = 0
    while i < photo_count:
        print("CAPTURING IMG #" + str(i))
        filename = capture(1280, 720, i, job_dir)
        print("SENDING " + filename)
        if filename != "":
            client.send_photo(job_dir + "/" + filename)
        i+=1
            
    return

def main():
    print("STARTING CAPTURE AND SENDING OF PHOTOS TO REMOTE SERVER")
    capture_and_send_series(DEFAULT_PHOTO_COUNT, CAPTURE_JOB_DIR)
    print("FINISHED SENDING PHOTOS TO SERVER. CLOSING CLIENT APP")

if __name__ == "__main__":
    main()
