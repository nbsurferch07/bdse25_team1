import fengshui_detect
import cv2


# path need to be changed
path = "C:\\Users\\Student\\BDSE25_30\\99_Projects\\Final_Project\\03_Execution\\03_img_recognition\\images\\44.jpg"
img = cv2.imread(path)
# remove noise
img = fengshui_detect.remove_noise(img)

output_img = img.copy()


# Fengshui 1
# check if the door is opposite the other door 
output_img, flag1 = fengshui_detect.check_FengShui_1(img, output_img)


# Fengshui 2
# check if the wrong room size exists
output_img, flag2 = fengshui_detect.check_FengShui_2(img, output_img)


# Fengshui 3
# check if the bathroom is in the middle of the room
output_img, flag3 = fengshui_detect.check_FengShui_3(img, output_img)

cv2.imshow("input image", img) # original image
cv2.imshow("check door image", output_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
