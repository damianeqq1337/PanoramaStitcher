import cv2
import imutils
import numpy as np

class Stitcher:
    def runStitcher(self, images):
        result = None
        loadedImages = []
        for imageNumber in range(0, len(images)):
            image = cv2.imread(images[imageNumber], 1)
            image = imutils.resize(image, width=400)
            loadedImages.append(image)
        for im in range(len(loadedImages)):
            if result is None:
                result = self.stitch(loadedImages[im], loadedImages[im+1])
                continue
            else:
                if (im+1) == len(loadedImages):
                    break
            result = self.stitch(result, loadedImages[im+1])
        cv2.imshow('result',result)
        cv2.waitKey(0)

        return None

    def match(self,imageA,imageB):
        
        descriptor = cv2.xfeatures2d.SIFT_create()
        (kpsA, featuresA) = descriptor.detectAndCompute(imageA, None)
        (kpsB, featuresB) = descriptor.detectAndCompute(imageB, None)
        
        kpsA = np.float32([kp.pt for kp in kpsA])
        kpsB = np.float32([kp.pt for kp in kpsB])

        matcher = cv2.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []
        
        for m in rawMatches:
            if len(m) == 2 and m[0].distance < m[1].distance * 0.75:
                matches.append((m[0].trainIdx, m[0].queryIdx))
                
        if len(matches) > 4:
            ptsA = np.float32([kpsA[i] for (_,i) in matches])
            ptsB = np.float32([kpsB[i] for (i,_) in matches])
            
            (H, status) = cv2.findHomography(ptsB, ptsA, cv2.RANSAC,4)
            return H
            
        return None



    def stitch(self,imgA,imgB):

        H = self.match(imgA,imgB)

        (xmax,ymax,xmin,ymin) = self.find_dimensions(imgA,imgB,H)

        t = [-xmin,-ymin]
        Ht = np.array([[1,0,t[0]],[0,1,t[1]],[0,0,1]])

        if xmin >= 0 and ymin >= 0:

            result = cv2.warpPerspective(imgB, H,(xmax,ymax)) 

            result = self.filter_blackpixels(imgA,result)


        if xmin < 0 and ymin >= 0:

            result = cv2.warpPerspective(imgB, Ht.dot(H),(xmax-xmin,ymax))   

            corrected_result = np.zeros((ymax+ymin, xmax-xmin, 3), np.uint8)

            corrected_result[ymin:ymax+ymin,0:xmax] = result[0:ymax,0:xmax]

            corrected_input = np.zeros((imgA.shape[0],imgA.shape[1]-xmin,3), np.uint8)

            corrected_input[0:imgA.shape[0],-xmin:imgA.shape[1]-xmin] = imgA[0:imgA.shape[0],0:imgA.shape[1]]

            # cv2.imshow('result_corrected',corrected_result)
            # cv2.imshow('input_corrected',corrected_input)



            result = self.filter_blackpixels(corrected_input,corrected_result)

        if xmin >= 0 and ymin <0:

            result = cv2.warpPerspective(imgB, Ht.dot(H),(xmax,ymax-ymin))   

            corrected_result = np.zeros((ymax-ymin, xmax+xmin, 3), np.uint8)

            corrected_result[0:ymax,xmin:xmax+xmin] = result[0:ymax,0:xmax]

            corrected_input = np.zeros((imgA.shape[0]-ymin,imgA.shape[1],3), np.uint8)

            corrected_input[-ymin:imgA.shape[0]-ymin,0:imgA.shape[1]] = imgA[0:imgA.shape[0],0:imgA.shape[1]]

            # cv2.imshow('result_corrected',corrected_result)
            # cv2.imshow('input_corrected',corrected_input)



            result = self.filter_blackpixels(corrected_input,corrected_result)

        if xmin < 0 and ymin <0 :

            result = cv2.warpPerspective(imgB, Ht.dot(H),(xmax-xmin,ymax-ymin))   

            # corrected_result = np.zeros((ymax-ymin, xmax-xmin, 3), np.uint8)

            # corrected_result[-ymin:ymax-ymin,-xmin:xmax-xmin] = result[0:ymax,0:xmax]

            corrected_input = np.zeros((imgA.shape[0]-ymin,imgA.shape[1]-xmin,3), np.uint8)

            corrected_input[-ymin:imgA.shape[0]-ymin,-xmin:imgA.shape[1]-xmin] = imgA[0:imgA.shape[0],0:imgA.shape[1]]

            cv2.imshow('result_corrected',result)
            cv2.imshow('input_corrected',corrected_input)



            result = self.filter_blackpixels(corrected_input,result)



        # cv2.imshow('warpedimage',result)





        #cv2.imshow('warpedimage',result)
        #cv2.imshow('leweimage',imgB)

        return result

    def find_dimensions(self,imgA,imgB,H):

        heightA = imgA.shape[0]
        heightB = imgB.shape[0]
        
        widthA = imgA.shape[1]
        widthB = imgB.shape[1]

        dimensions_vector = ((0,widthB,widthB,0),(0,0,heightB,heightB),(1,1,1,1))


        dimensions_matrix = np.matrix(dimensions_vector)


        dimansions_matrix_warped = np.dot(H,dimensions_matrix)

        wiersz1 = dimansions_matrix_warped[0,:]
        wiersz2 = dimansions_matrix_warped[1,:]
        wiersz3 = dimansions_matrix_warped[2,:]

        wiersz1 = np.divide(wiersz1,wiersz3)
        wiersz2 = np.divide(wiersz2,wiersz3)

        maxx = int(np.max(wiersz1))
        maxy = int(np.max(wiersz2))

        minx = int(np.min(wiersz1))
        miny = int(np.min(wiersz2))

        if maxx < widthA:
            maxx = widthA
        if maxy < heightA:
            maxy = heightA

        return (maxx,maxy,minx,miny)







    def filter_blackpixels(self,imageA,imageB):

        Ah , Aw = imageA.shape[:2]
        Bh , Bw = imageB.shape[:2]


        for i in range (0,Aw):
            for j in range (0,Ah):
                try:
                    if not(np.array_equal(imageA[j,i],np.array([0,0,0]))):
                        imageB[j,i] = imageA[j,i]
                except:
                    pass
        return imageB