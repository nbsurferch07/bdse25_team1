# Import library
from detection_testing.utils.FloorplanToBlenderLib import *
import math
import random 
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import cv2 # for image gathering
from matplotlib import pyplot as plt
import pytesseract
from IPython.display import display



# ------------------------------------------------------------



# Set function

def remove_noise(img):
    # get binary image
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to gray
    thresh = cv2.threshold(img_gray, 135, 255, cv2.THRESH_BINARY)[1] # convert to binary
    img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    
    # contour hierarchy
    regions, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # detect all elements
    countour_list = []
    for region in regions:
        x, y, w, h = cv2.boundingRect(region)
        countour_list.append([x, y, w, h])
    
    # get 2nd largest contour
    countour_list = np.asarray(countour_list)  # convert to numpy-array
    column_values = ['left', 'top', 'width', 'height']
    df = pd.DataFrame(data = countour_list, columns = column_values)
    df = df.sort_values(by='width', ascending=False)

    index = df.iloc[1]
    x, y, w, h = index['left'], index['top'], index['width'], index['height']

    
    # remove outside noise
    img[:, :x] = [255, 255, 255]
    img[x + w + 1:, :] = [255, 255, 255]
    img[:y, :] = [255, 255, 255]
    img[y + h + 1:, :] = [255, 255, 255]
    
    return img



def impl_model(img):
    # get words position
    result = reader.readtext(img,
                             detail=1,
                             paragraph=True, # Combine result into paragraph
                             x_ths=0.1, # Maximum horizontal distance to merge text boxes when paragraph=True
                             y_ths=0.5, # Maximum verticall distance to merge text boxes when paragraph=True
                             # width_ths=0.1,
                             # height_ths=0.1,
                             mag_ratio=1.2,
                             )
    return result



def correct_name_for_bath(result):
    # correct to the right room name
    bed_room = ['堅', '臥 室', '臥 堂', '室', '臥室']
    bth_room = ['瑜', '}', '沿廁', '浴廁','淞廁','汗廝']
    d_room = ['餐廳']
    l_room = ['客廳']
    kit = ['麝','房', '廚房']
    bal=['陽=','陽^','陽台']
    for i in range(len(result)): 

        if result [i][-1] in bed_room: result [i][-1] = '臥室' # bedroom

        elif result [i][-1] in bth_room: result [i][-1] = '浴廁' # bathroom

        elif result [i][-1] in d_room: result [i][-1] = '餐廳' # dining room

        elif result [i][-1] in l_room: result [i][-1] = '客廳' # living room

        elif result [i][-1] in kit: result [i][-1] = '廚房' # kitchen

        elif result [i][-1] in bal: result [i][-1] = '陽台' # kitchen

        else: result [i][-1] = '其他' # others

    return result



def get_words_position():
    c_list = []
    
    # length = len(c_n_result)
    for i in c_n_result:
        # img_array.append(i[0]) 
        # room_name.append(i[1]) # get room type array
        
        # get center of each word
        x = (i[0][1][1] + i[0][2][1]) / 2  # gey x
        y = (i[0][0][0] + i[0][1][0]) / 2  # get y
        
        # put in center of gravity list
        c_list.append([[y, x], i[1]])

    return c_list





def get_boxes(img):
    # get boxes
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = detect.wall_filter(gray)

    gray = ~gray

    rooms, colored_rooms = detect.find_rooms(gray.copy())

    gray_rooms =  cv2.cvtColor(colored_rooms, cv2.COLOR_BGR2GRAY)

    # get box positions for rooms
    boxes, gray_rooms = detect.detectPreciseBoxes(gray_rooms, gray_rooms)
    
    return boxes, gray_rooms



def get_room_list(img, c_list):
    room_list = []
    
    boxes, gray = get_boxes(img)
    
    for i in boxes:
        new_arr = np.reshape(np.ravel(i), (-1, 2)) # equivalent to C ravel then C reshape
        box = new_arr.tolist() # convert to python scalar

        polygon = Polygon(box)

        for j in c_list:
            point = Point(j[0])
            if polygon.contains(point):
                room_list.append([box, j[1]])
    
    return room_list



def find_bath_rectangle(room_list):
    i =0
    bath_rectangle=[]
    for i in range(len(room_list)):      
        if '浴廁' in (room_list) [i][-1]:
            bath=((room_list)[i][:-1])
            bath_rectangle.append(bath)
    bath_rectangle = np.array(bath_rectangle)
    return bath_rectangle



def center_point(test3):
    # Create blank imag
    height, width, channels = test3.shape
    blank_image = np.zeros((height,width,3), np.uint8)

    # Grayscale image
    gray = cv2.cvtColor(test3,cv2.COLOR_BGR2GRAY)

    # detect outer Contours (simple floor or roof solution), paint them red on blank_image
    contour, test3 = detect.detectOuterContours(gray, blank_image, color=(255,0,0))
    c = contour
    mv = cv2.moments(c)
    center_x = int(mv['m10']/mv['m00'])
    center_y = int(mv['m01']/mv['m00'])
    center_point = (center_x,center_y)
    
    return center_point

# ------------------------------------------------------------

# Run the main program


# this needs to run only once to load the model into memory
global reader
reader = easyocr.Reader(['ch_tra','en'])



# load image

img = cv2.imread("detection_testing/Images/test5.jpg")

cv2.imshow("original_img", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# ------------------------------------------------------------

# process
img = remove_noise(img)

cv2.imshow("remove_noise_img", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

result = impl_model(img)

c_n_result = correct_name_for_bath(result)

c_list = get_words_position()

test = img.copy()

boxes, gray_rooms = get_boxes(img)

room_list = get_room_list(img, c_list)

bath_rectangle = find_bath_rectangle(room_list)

# ------------------------------------------------------------

test2 = img.copy()

test2 = cv2.polylines(test2,bath_rectangle,True, (0, 0, 255), 2)

cv2.imshow("paint_bath_rectangle_ing", test2)
cv2.waitKey(0)
cv2.destroyAllWindows()

# ------------------------------------------------------------

test3 = img.copy()

center_point = center_point(test3)

# Search center point
paint_center_point = cv2.circle(test2,center_point,10,(0,0,255),-1,0)

cv2.imshow("paint_center_point_img", paint_center_point)
cv2.waitKey(0)
cv2.destroyAllWindows()

# ------------------------------------------------------------
# Check fengshui
for i in bath_rectangle:
    a = cv2.pointPolygonTest(i, center_point, False)
    if a == 1.0:
        print("浴廁居中")
        
    elif a == 0.0:
        print("浴廁居中")
        
    elif a == -1.0:
        print("浴廁並無居中")