import os
import settings
import cv2
import numpy as np
from imutils.perspective import four_point_transform 

def save_upload_image(fileObj):
    filename = fileObj.filename
    # name, ext = filename.split('.')
    # save_filename = 'upload.'+ext
    
    upload_image_path = settings.join_path(settings.SAVE_DIR, filename)
    
    fileObj.save(upload_image_path)
    
    return upload_image_path

class DocumentScan():
    def __init__(self):
        pass

    
    def document_scanner(self, image_path):
        self.image = cv2.imread(image_path)
        img_re, self.size = self.resizer(self.image)

        try:
            detail = cv2.detailEnhance(img_re, sigma_s=20, sigma_r=0.15)
            gray = cv2.cvtColor(detail, cv2.COLOR_BAYER_BG2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5),0)
            #edges
            edge_image = cv2.Canny(blur, 75, 200)
            #morphological transform
            kernel = np.ones((5,5), np.uint8)
            dilate = cv2.dilate(edge_image, kernel, iterations=1)
            closing = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
            #find contours
            contours, hire = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            for contour in contours:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02*peri, True)
                
                if len(approx)==4:
                    four_points = np.squeeze(approx)
                    break
            
            return four_points, self.size
        
        except:
            return None, self.size
        
    
    def calibrate_to_original_size(self, four_points):
          #fours points for original image
        multiple = self.image.shape[1]/self.size[0]
        four_points_orig = four_points*multiple
        four_points_orig = four_points_orig.astype(int)
        
        wrap_image = four_point_transform(self.image, four_points_orig)
        #apply magic colour
        magic_color = self.apply_brightness_contrast(wrap_image, brightness=40, contrast=40)
        
        return magic_color