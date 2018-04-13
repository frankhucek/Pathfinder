# This module provides the function capture()
# Provide capture with relevant parameters including
# resolution, photo_number, job directory, and job number, and it will take and save the
# photos to their specified locations

import time
import picamera

def capture(resolutionX, resolutionY, photo_number, job_directory):
    with picamera.PiCamera() as camera:
        camera.resolution = (resolutionX,resolutionY)
        camera.start_preview()
        # Camera init time slightly > 1 second
        time.sleep(2)
        filename = "job" + job_directory[-1] + "_" + str(photo_number) + ".jpg"
        camera.capture(job_directory + "/" + filename)
    return
# usage:
# capture(1024, 768, 0, "jobs/0")
