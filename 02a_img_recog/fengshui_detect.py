import detect
import cv2
import numpy as np
import pandas as pd
import math
import easyocr
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
# import random
# import ctypes

"""
Detect
This file contains functions used when detecting and calculating shapes in images.

FloorplanToBlender3d
Copyright (C) 2019 Daniel Westberg

Floor-Plan-Detection
Copyright (c) 2021 Resilience Business Grids
"""

def remove_noise(img):
    """
    Remove watermark and outer noise from image
    @Param @mandatory img image input
    @Return processed image
    """
    # step1 get binary image to remove watermark 
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to gray
    thresh = cv2.threshold(img_gray, 135, 255, cv2.THRESH_BINARY)[1] # convert to binary
    img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    

    # step2 remove outer noise
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


def img_processing(img):
    """
    I have copied and changed this function

    origin from 
    https://stackoverflow.com/a/62317418

    @Param img input image
    @Return thresh: get a grayscale image for which a threshold calculation has been performed
            marker: repeated eroding and dilating to filter contours
            walls: get a grayscale image for which by eroding only the contour of the room exist
            others: get a greyscale image with filtered elements on a black background 
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # convert to binary image & remove noise
    thresh = gray

    #  Morphological reconstruction (delete labels)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    marker = cv2.dilate(thresh, kernel, iterations = 1)
    while True:
        tmp = marker.copy()
        marker = cv2.erode(marker, kernel2)
        marker = cv2.max(thresh, marker)
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
    """
    Get median value of elements width & height
    Help function for FengShui checking
    @Param data for the list of all detected elements
    @Return width and height value
    """
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


def find_door_list(img):
    """
    I have copied and changed this function

    origin from 
    https://stackoverflow.com/a/62317418

    Help function for FengShui-1 checking 
    @Param image input image
    @Return center point of doors
    """  
    cp_list = []
    
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
            cp_list.append([cx, cy])

    return cp_list


def swap(v1, v2):
    tmp = v1
    v1 = v2
    v2 = tmp
    return v1, v2


def check_wall(wall, coord):
    """
    Check the pixels of the wall elements in the image
    Help function for error line checking
    @Param wall image input
    @Param coord the specific coordinates of the walls
    @Return true as white, black as black
    """
    val = wall[coord[1], coord[0]]  # img(y, x)

    # 0 -> False / 255 -> True
    return True if val else False


def check_door(other, coord):
    """
    Check the pixels of the door elements in the image
    Help function for error line checking
    @Param other image input
    @Param coord the specific coordinates of the doors
    @Return true as white, false as black
    """
    for x in range(coord[0] - 1, coord[0] + 2):
        for y in range(coord[1] - 1, coord[1] + 2):
            val = other[y, x]  # img(y, x)
            # print([x, y], val)
            
            if val: return True # 0 -> True / 255 -> False
            
    return False


def check_error_line(img, p1, p2):
    """
    Check whether the error line can be drawn
    Help function for FengShui 1 checking
    @Param img input image
    @Param p1 check point 1
    @Param p2 check point 2
    @Return true as there exist detected fengshui, false as not exists 
    """
    # wall for boundary detection / other for door detection
    _, _, walls, other = img_processing(img)
    
    
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    
    pt_list = []
    
    # when y = 0
    if dx == 0:
        ang = 90
        x = p1[0]
        
        # swap value when p1 > p2
        if p1[1] > p2[1]:
            p1, p2 = swap(p1, p2)
        
        # detection range of the line extended
        for y in range(p1[1] - 15, p2[1] + 15):
            pt = [x, y]
            
            # boundary detection
            if not check_wall(walls, pt):
                return False
            
            # misidentified door excluded
            if check_door(other, pt):
                # check if any similar point exists in the list
                if not pt_list or abs(sum(pt) - sum(pt_list[-1])) > 5: 
                    pt_list.append(pt)
                else: pass
                
    # when y != 0
    else:
        m = dy / dx  # get slope
        arc = math.atan(abs(m))  # get arc
        ang = (arc * 180) / math.pi  # get angle
        
        a = m
        b = p1[1] - a*p1[0]

        # x-axis
        if ang < 7:
            
            # swap value when p1 > p2
            if p1[0] > p2[0]:
                p1, p2 = swap(p1, p2)
            
            # detection range of the line extended
            for x in range(p1[0] - 15, p2[0] + 15):
                y = int(a*x + b)
                pt = [x, y]
                
                # boundary detection
                if not check_wall(walls, pt):
                    return False
                
                # misidentified door excluded
                if check_door(other, pt):
                    # check if any similar point exists in the list
                    if not pt_list or abs(sum(pt) - sum(pt_list[-1])) > 5: 
                        pt_list.append(pt)
                    else: pass
                    
                
        # y-axis
        elif ang > 83:
            
            # swap value when p1 > p2
            if p1[1] > p2[1]:
                p1, p2 = swap(p1, p2)
            
            # detection range of the line extended
            for y in range(p1[1] - 15, p2[1] + 15):
                x = int((y - b) / a)
                pt = [x, y]
                
                # boundary detection
                if not check_wall(walls, pt):
                    return False
                
                # misidentified door excluded
                if check_door(other, pt):
                    # check if any similar point exists in the list
                    if not pt_list or abs(sum(pt) - sum(pt_list[-1])) > 5: 
                        pt_list.append(pt)
                    else: pass
                
        else: return False

    # print(pt_list)
    if len(pt_list) > 2: return False
    
    return True
    
    

def impl_model(img):
    """
    Implementing the easyocr model 
    Help function for FengShui 2 and 3 checking
    @Param image input image
    @Return result the detected word list from the model
    """
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
    """
    Get the midpoint of all recognised words
    Help function for FengShui 2 and 3 checking
    @Param image input image
    @Return midpoint list
    """
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
    """
    Get the midpoint of all recognised words
    Help function for FengShui 2 and 3 checking
    @Param image input image
    @Return coordinates of the room in the list and grayscale room image
    """
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
    """
    Correct the detected wrong room name
    Help function for FengShui 2 and 3 checking
    @Param val input room type string
    @Return corrected room type string
    """
    # correct to the right room name
    bed_room = ['堅', '臥 室', '臥 堂', '室', '臥室']
    bth_room = ['瑜', '}', '沿廁', '淞廁', '汗廝', '浴廁']
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
    """
    Get related information
    @Param img image input
    @Param selected room type
    @Return coordinates and area of the room in list
    """
    # get room coordinate and type
    room_dict = get_room_dict(img)
    
    # get coordinate(s) of specific room type
    info_list = room_dict[select_room_type]
        
    return info_list


def contour_drawing(img, err_list):
    """
    Drawing for signature where fengshui problem exists
    Help function for FengShui-2 and FengShui-3 checking 
    @Param image input image
    @Param error list for a specific room coordinate
    @Return output image
    """  
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
    
    return img


def get_center_point(img):
    """
    Drawing for signature where fengshui problem exists
    Help function for FengShui-3 checking 
    @Param image input image
    @Return center point of room
    """  
    # Create blank imag
    height, width, channels = img.shape
    blank_image = np.zeros((height,width,3), np.uint8)

    # Grayscale image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # detect outer Contours (simple floor or roof solution), paint them red on blank_image
    contour, _ = detect.detectOuterContours(gray, blank_image, color=(255,0,0))
    
    mv = cv2.moments(contour)
    cx = int(mv['m10'] / mv['m00'])
    cy = int(mv['m01'] / mv['m00'])
    cp = (cx, cy)
    
    return cp


def check_FengShui_1(img, output_img):
    """
    Check if the door is opposite the other door
    @Param image input image for fengshui checking
    @Return output image
    """
    flag = 0 # check whether exists fengshui-1

    cp_list = find_door_list(img)
    for i in range(len(cp_list) - 1):
        for j in range(i + 1, len(cp_list)):
            if check_error_line(img, cp_list[i], cp_list[j]):  # if true -> draw the line
                flag = 1
                cv2.line(output_img, cp_list[i], cp_list[j], (0, 0, 255), 5)
                
    return output_img, flag


def check_FengShui_2(img, output_img):
    """
    Check if the wrong room size exists
    @Param image input image for fengshui checking
    @Return output image
    """
    room_dict = get_room_dict(img)
    
    # set list for bedroom & living room
    b_list = room_dict['臥室']
    l_list = room_dict['客廳']

    # set list for bedroom & kitchen
    bth_list = room_dict['浴廁']
    kit_list = room_dict['廚房']

    flag = 0    
    err_list = []

    # check wether bedroom > living room
    for i in b_list:
        for j in l_list:
            if i[1] > j[1]:
                if i[1] not in err_list: err_list.append(i[0])
                if j[1] not in err_list: err_list.append(j[0])
    
    # check wether bathroom > kitchen
    for i in bth_list:
        for j in kit_list:
            if i[1] > j[1]:
                if i[1] not in err_list: err_list.append(i[0])
                if j[1] not in err_list: err_list.append(j[0])

    if err_list:
        flag = 1
        output_img = contour_drawing(output_img, err_list)


    return output_img, flag


def check_FengShui_3(img, output_img):
    """
    Check if the bathroom is in the middle of the room
    @Param image input image for fengshui checking
    @Return output image and boolean sign
    """
    flag = 0
    err_list = []
    
    # get bathroom list
    select_room_type = '浴廁'
    bth_list = get_info(img, select_room_type)
    
    
    # get center point of room
    cp = get_center_point(img)
    
    for bth in bth_list:
        bth_np_arr = np.array(bth[0])
        check_inner = cv2.pointPolygonTest(bth_np_arr, cp, False) # >=0 : inner / <0 : outer
        if check_inner >= 0: err_list.append(bth[0])

    if err_list:
        flag = 1
        output_img = contour_drawing(output_img, err_list)
    
    return output_img, flag


# Only needs to run once to load the model into memory
global reader
reader = easyocr.Reader(['ch_tra','en']) 