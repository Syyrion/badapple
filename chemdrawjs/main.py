import os
from svgparser import svgtomol
from chemdraw import ChemDraw
import cv2 as cv
import numpy as np
import datetime
from selenium.common.exceptions import *
import logging

FRAMES = 6572
FRAMERATE = 30

SIZE = (4800, 3600)
SCALE = (0.0075, 0.0075)
OUTPUT_RESOLUTION = (1440, 1080)

MAX_ATTEMPTS = 3

MAX_API_CALLS = 100

LOGGING_LEVEL = logging.INFO

def main():
    log = getlogger("log.txt")

    cd = ChemDraw()
    video = cv.VideoWriter("chemdraw.avi", 0, FRAMERATE, OUTPUT_RESOLUTION)

    starttime = datetime.datetime.now()
    log.info("Begin Encoding")

    totalerrors = 0
    totalapicalls = 0

    for i in range(FRAMES):
        log.info(f"Processing frame {i + 1:d}/{FRAMES:d}.")
        
        apicalls = cd.getapicalls()
        if apicalls > MAX_API_CALLS:
            totalapicalls += apicalls
            log.info(f"Max API calls exceeded ({apicalls}/{MAX_API_CALLS}). Resetting... | API Calls: {totalapicalls}")
            cd.reset()

        framestarttime = datetime.datetime.now()
        
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            try:

                mol = svgtomol(f"../svg/frame{i + 1:0>6d}.svg")
                mol.createframe(SIZE)
                
                cd.uploadmol(mol.getstring(SCALE))
                image = cd.downloadimage(OUTPUT_RESOLUTION)
                
                video.write(np.array(image.convert("RGB")))
                break
            except Exception as e:
                exce = e
                log.warning(f"WebDriver error. Resetting... | Attempt: {(attempts := attempts + 1)}/{MAX_ATTEMPTS} | Total Errors: {(totalerrors := totalerrors + 1)}")
                cd.reset()

        frameendtime = datetime.datetime.now()

        log.info(f"Completed frame in {str(frameendtime - framestarttime)}. | Completion: {(i + 1) / FRAMES * 100:.2f}% | Elapsed time: {str(frameendtime - starttime)}")

        if attempts == MAX_ATTEMPTS:
            break
    

    cv.destroyAllWindows()
    video.release()

    totalapicalls += cd.getapicalls()
 
    log.info("End Encoding")
    log.info(f"Total elapsed time: {str(datetime.datetime.now() - starttime)} | API Calls: {totalapicalls} | Errors: {totalerrors}")
    
    cd.quit()

    if attempts == MAX_ATTEMPTS:
        raise exce

def getlogger(logfile):
    log = logging.getLogger(__name__)
    log.setLevel(LOGGING_LEVEL)

    fmt = logging.Formatter("%(asctime)s - %(levelname)s || %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(LOGGING_LEVEL)
    ch.setFormatter(fmt)

    fh = logging.FileHandler(filename=logfile, mode="w")
    fh.setLevel(LOGGING_LEVEL)
    fh.setFormatter(fmt)

    log.addHandler(ch)
    log.addHandler(fh)
    return log

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    main()