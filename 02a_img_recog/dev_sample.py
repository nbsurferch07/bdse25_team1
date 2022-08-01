import fengshui
import cv2
# from utils.FloorplanToBlenderLib import *
# from PIL import Image
# import numpy as np
# import pandas as pd
# import math
# import easyocr
# from shapely.geometry import Point
# from shapely.geometry.polygon import Polygon
# import random
# import ctypes


# path need to be changed
img = cv2.imread("C:\\Users\\Student\\BDSE25_30\\99_Projects\\Final_Project\\03_Execution\\03_img_recognition\\images\\44.jpg")
# process
img = fengshui.remove_noise(img)
cv2.imshow("img", img)
cv2.waitKey(0)
cv2.destroyAllWindows()


# Fengshui 1
check_door_img = img.copy() 

# get doors coordinate
c_list = fengshui.find_door(check_door_img)

# check fengshui & draw the signal
res_img = fengshui.check_FengShui_1(c_list, check_door_img)


# res_img = res_img.astype('float32') / 255
cv2.imshow("res_img", res_img)
cv2.waitKey(0)
cv2.destroyAllWindows()



# Fengshui 2
check_room_img = img.copy() 

err_list = fengshui.check_room_size(check_room_img)

fengshui.contour_drawing(check_room_img, err_list)

cv2.imshow("check_img", check_room_img)
cv2.waitKey(0)
cv2.destroyAllWindows()