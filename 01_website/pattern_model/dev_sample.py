from app import UPLOAD_FOLDER
from pattern_model import fengshui_detect
import cv2


def pattern_recog(img_name):
    # path need to be changed
    path = 'pattern_img/'+img_name
    img = cv2.imread('./static/'+path)
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

    path_index = path.find('.jpg')
    result_path = path[:path_index] +'_result'+ path[path_index:]
    cv2.imwrite('./static/'+result_path, output_img)

    return flag1, flag2, flag3, result_path

# cv2.imshow("input image", img) # original image
# cv2.imshow("check door image", output_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
