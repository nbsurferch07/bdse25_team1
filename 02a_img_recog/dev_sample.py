import fengshui
import cv2


# path need to be changed
path = "C:\\Users\\Student\\BDSE25_30\\99_Projects\\Final_Project\\03_Execution\\03_img_recognition\\images\\5.jpg"
img = cv2.imread(path)
img = fengshui.remove_noise(img)



# Fengshui 1
check_door_img = img.copy()
# check if the door is opposite the other door 
check_door_img = fengshui.check_FengShui_1(check_door_img)


# Fengshui 2
check_room_img = img.copy() 
# check if the wrong room size exists
room_err_list = fengshui.check_FengShui_2(check_room_img)


# Fengshui 3
check_bth_img = img.copy() 
# check if the bathroom is in the middle of the room
check_bth_img = fengshui.check_FengShui_3(check_bth_img)

cv2.imshow("input image", img) # original image
cv2.imshow("check door image", check_door_img)
cv2.imshow("check room image", check_room_img)
cv2.imshow("check bathroom image", check_bth_img)

cv2.waitKey(0)
cv2.destroyAllWindows()