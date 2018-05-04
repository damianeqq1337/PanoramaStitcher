import sys
import imutils
import numpy as np
import cv2

class ShowWindow:
    def __init__(self, path):
        self.path = path

    def showImage(self):
        img = cv2.imread(self.path)
        img = imutils.resize(img, width=400)
        cv2.imshow(self.path, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    