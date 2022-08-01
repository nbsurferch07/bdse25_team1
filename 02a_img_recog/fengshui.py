from utils.FloorplanToBlenderLib import *
import cv2
import numpy as np
import pandas as pd
import math
import easyocr
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
# import random
# import ctypes


# Fengshui 1
def img_processing(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # convert to binary image & remove noise
    thresh = cv2.threshold(gray, 135, 255, cv2.THRESH_BINARY )[1]

    #  Morphological reconstruction (delete labels)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    marker = cv2.dilate(thresh, kernel, iterations = 1)
    while True:
        tmp=marker.copy()
        marker=cv2.erode(marker, kernel2)
        marker=cv2.max(thresh, marker)
        difference = cv2.subtract(tmp, marker)
        if cv2.countNonZero(difference) == 0:
            break

    # only walls
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    walls = cv2.morphologyEx(marker, cv2.MORPH_CLOSE, se)
    walls = cv2.erode(walls, kernel2, iterations = 2)

    # other objects
    other = cv2.compare(marker,walls, cv2.CMP_GE)
    other = cv2.bitwise_not(other)
    return thresh, marker, walls, other


def get_median(data):
    # get median of elements width & height
    column_values = ['left', 'top', 'width', 'height', 'area']
    df = pd.DataFrame(data = data, columns = column_values)
    df = df[(df['width'] >= 10) & 
            (df['height'] >= 10) & 
            (df['width'] < 50) & 
            (df['height'] < 50)].sort_values(by='width', ascending=True)
    
    m_width = df['width'].median()
    m_height = df['height'].median()
    return m_width, m_height


def find_door(img):
    c_list = []
    
    thresh, marker, walls, other = img_processing(img)

    # find connected components and select by size and area
    output = cv2.connectedComponentsWithStats(other, 4, cv2.CV_32S)
    num_labels = output[0]
    labels = output[1]
    stats = output[2]
    centroids = output[3]
    
    m_width, m_height = get_median(stats)
    
    for i in range(num_labels):
        left, top, width, height, area = stats[i]
        if width > m_width - 10 and width < m_width + 10 and height > m_height - 10 and height < m_height + 10 and abs(width - height) < 15:
            # door gravity
            cx = round(left + width*0.5)
            cy = round(top + height*0.5) 
            c_list.append([cx, cy])

    return c_list


def check_rgb(img, coord):
    val = img[coord[1], coord[0]]  # img(y, x)
    
    # black -> False / others -> True
    return True if sum(val) else False


def check_intersection(img, p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    
    
    # when y = 0
    if dx == 0:
        ang = 90
        x = p1[0]
        
        for y in range(p1[1], p2[1]):
            pt = [p1[0], y]
            # check if intersect wall
            if not check_rgb(img, pt):
                return False
    # when y != 0
    else:
        m = dy / dx  # get slope
        arc = math.atan(abs(m))  # get arc
        ang = (arc * 180) / math.pi  # get angle
        
        a = m
        b = p1[1] - (a * p1[0])

        # x-axis
        if ang < 6:
            if p1[0] > p2[0]:
                tmp = p1
                p1 = p2
                p2 = tmp
                
            for x in range(p1[0], p2[0]):
                y = round(a * x + b)
                pt = [x, y]
                if not check_rgb(img, pt):
                    return False

        # y-axis
        elif ang > 84:
            if p1[1] > p2[1]:
                tmp = p1
                p1 = p2
                p2 = tmp
                
            for y in range(p1[1], p2[1]):
                x = round((y - b) / a)
                pt = [x, y]
                
                if not check_rgb(img, pt):
                    return False
        else: return False
    
    return True
    
    
def check_FengShui_1(c_list, img):
    _, _, walls, _ = img_processing(img)
    walls = cv2.cvtColor(walls, cv2.COLOR_GRAY2BGR)
    
    for i in range(len(c_list) - 1):
        for j in range(i + 1, len(c_list)):
            if check_intersection(walls, c_list[i], c_list[j]):  # if true -> draw the lin
                cv2.line(img, c_list[i], c_list[j], (0, 0, 255), 5)
    
    return img


# Fengshui 2
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




def get_words_position(img):
    cp_list = []
    
    # load easyocr to get words position
    words_pos = impl_model(img)
    
    for word in words_pos:
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
    bth_room = ['瑜', '}', '沿廁', '浴廁']
    d_room = ['餐廳']
    l_room = ['客廳']
    kit = ['麝','房', '廚房']
    
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



def check_room_size(img):
    room_dict = get_room_dict(img)
    
    # set list for bedroom & living room
    b_list = room_dict['臥室']
    l_list = room_dict['客廳']

    # set list for bedroom & kitchen
    bth_list = room_dict['浴廁']
    kit_list = room_dict['廚房']
    
    err_list = []
    # check wether bedroom > living room
    for i in b_list:
        for j in l_list:
            if i[1] > j[1]:
                # print(f'臥室 > 客廳:\n{i[1]} > {j[1]}')
                # contour_drawing(img, i[0])
                # contour_drawing(img, j[0])
                if i[1] not in err_list: err_list.append(i[0])
                if j[1] not in err_list: err_list.append(j[0])
    
    # check wether bathroom > kitchen
    for i in bth_list:
        for j in kit_list:
            if i[1] > j[1]:
                # print(f'廁所 > 廚房:\n{i[1]} > {j[1]}')
                # contour_drawing(img, i[0])
                # contour_drawing(img, j[0])
                if i[1] not in err_list: err_list.append(i[0])
                if j[1] not in err_list: err_list.append(j[0])

    return err_list


def contour_drawing(img, err_list):
    
    if err_list:
        print('gotcha')
        
        i = 0
        while i < len(err_list):
            pts = np.array(err_list[i])

            img = cv2.polylines(img,
                                [pts],
                                True, # isClosed
                                (0, 0, 255), # color
                                2, # thickness
                               )
            i += 1
    else: print('not find error')
    
    return img


# Only needs to run once to load the model into memory
global reader
reader = easyocr.Reader(['ch_tra','en']) 