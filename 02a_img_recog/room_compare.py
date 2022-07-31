from utils.FloorplanToBlenderLib import *
from PIL import Image
import cv2
import numpy as np
import pandas as pd
import math
import easyocr
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
# import random
# import ctypes


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



def load_easyocr_model(img):
    # this needs to run only once to load the model into memory
    reader = easyocr.Reader(['ch_tra','en']) 
    
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



def get_words_position(img):
    cp_list = []
    
    # load easyocr to get words position
    words_result = load_easyocr_model(img)
    
    for word in words_result:        
        # get center point of each word
        x = (word[0][1][1] + word[0][2][1]) / 2  # gey x
        y = (word[0][0][0] + word[0][1][0]) / 2  # get y
        
        # put in center of gravity list
        cp_list.append([[y, x], word[1]])

    return cp_list


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


def correct_name(val):
    # correct to the right room name
    bed_room = ['堅', '臥 室', '臥 堂', '室', '臥室']
    bth_room = ['瑜', '}', '浴廁']
    lk_room = ['裘', '更衣室']
    d_room = ['餐廳']
    l_room = ['客廳']
    kit = ['廚房']
    
    if val in bed_room: val = '臥室' # bedroom
        
    elif val in bth_room: val = '浴廁' # bathroom
        
    elif val in d_room: val = '餐廳' # dining room
        
    elif val in l_room: val = '客廳' # living room
        
    elif val in kit: val = '廚房' # kitchen
        
    else: val = '其他' # others
        
    return val


def get_room_dict(img):
    
    # build room dictionary
    room_dict = {
        '臥室':[],
        '浴廁':[],
        '餐廳':[],
        '客廳':[],
        '廚房':[],
        '其他':[],
    }
    
    # get room contour
    boxes, gray_rooms = get_boxes(img)
    
    # get center point of each room type
    cp_list = get_words_position(img)
    
    for box in boxes:
        area = cv2.contourArea(box)
        new_arr = np.reshape(np.ravel(box), (-1, 2)) # equivalent to C ravel then C reshape
        box = new_arr.tolist() # convert to python scalar
        
        # check whether the point in the box 
        polygon = Polygon(box)
        for cp in cp_list:
            point = Point(cp[0]) # cp[0] => coordinate 
            
            # if yes, add to the room dictionary
            if polygon.contains(point):
                val = correct_name(cp[1]) # check and correct to the right room name
                room_dict[val].append([box, area])

    return room_dict


def get_info(img, select_room_type):
    
    # get room coordinate and type
    room_dict = get_room_dict(img)
    
    # get coordinate(s) of specific room type
    info_list = room_dict[select_room_type]
        
    return info_list