# ! Depreciated

import cv2
import sys
import os
import shutil

def main():
    print('Frame Extractor Utility')

    while True:
        path = input('\nEnter path to file to extract.\nYou can also drag a file here to copy its path.\nType exit to close.\n')

        if path == 'exit':
            return

        directory = os.path.dirname(path)
        file = os.path.basename(path)

        os.chdir(directory)

        cap = cv2.VideoCapture(file)

        frameNum = 1

        if os.path.isdir('frames'):
            if input('\nFrames directory already exists\nDo you want to overwrite it? [Y/n]: ') == 'Y':
                shutil.rmtree('frames')
            else:
                print('Extraction aborted')
                continue        
        os.mkdir('frames')

        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print('\n\nExtraction completed')
                    break

                sys.stdout.write("\b" * 7)
                sys.stdout.write("%06d" % frameNum)
                sys.stdout.flush()

                cv2.imwrite("frames/frame%06d.png" % frameNum, frame)
                frameNum += 1

        except KeyboardInterrupt:
            print('\n\nExtraction aborted')

        cap.release()

if __name__ == '__main__':
    main()