import sys
import numpy as np
import cv2
import imutils
from matplotlib import pyplot as plt

img = cv2.imread('piesel.jpg')
img1 = cv2.imread('wiew.jpg')
vis = np.concatenate((img, img1), axis=1)
cv2.imwrite('out.png', vis)
cv2.imshow('image', vis)
cv2.waitKey(0)
cv2.destroyAllWindows()

class Stitcher:
    def initial(self):
        self.isv3 = imutils.is_cv3()
        pass


