import cv2
import numpy as np
import re

if __name__ != "__main__":
    from common.data import *

# функция, непосредственно обрабатывающая изображение
def edit_image(img, parameters, app_info):
    colors = ("red_traffic_light_before", "red_traffic_light_after_bright", "red_traffic_light_after_dark", 
    "yellow_traffic_light_bright", "yellow_traffic_light_dark", "green_traffic_light_bright", "green_traffic_light_dark")

    traffic_light_image = None
    traffic_light_image_hsv = None
    series = 0

    additional_data = app_info.get("additional_data")
    #print(additional_data)
    text = [x for x in additional_data if x["plugin"].startswith('Распознавание светофоров')][0]['text'].split('\n')
    our_traffic_light = text[parameters["traffic_light_number"] - 1]
    rectangle = re.match(r'Левая верхняя точка: \((\d+), (\d+)\), правая нижняя точка: \((\d+), (\d+)\)', our_traffic_light)

    calculated_color = None

    if not rectangle is None:
        rectangle = rectangle.groups()
        rectangle = (int(rectangle[0]), int(rectangle[1]), int(rectangle[2]), int(rectangle[3]))
        #print(rectangle)
        #traffic_light_image = np.zeros((boundRect[i][3]+2, boundRect[i][2]-2, 3), np.uint8)
        traffic_light_image = img[rectangle[1]+2:rectangle[3]-2, rectangle[0]+2:rectangle[2]-2]
        #cv2.imwrite(rf"C:\ProgramData\cv_experiments\temp\{kwargs.get('frame_index')}.bmp", traffic_light_image)
        shape = traffic_light_image.shape
        #print(shape)
        traffic_light_image_hsv = cv2.cvtColor(traffic_light_image, cv2.COLOR_BGR2HSV)
        pixels = [0, 0, 0] # красный, потом жёлитый, потом зелёный
        threshold = parameters['threshold'] # порог, при котором данный цвет вообще обнаруживается
        for j, color in enumerate(colors):
            pixel = np.count_nonzero(cv2.inRange(traffic_light_image_hsv, *get_boundaries_hsv(color)))
            if j == 0 or j == 1 or j == 2:
                pixels[0] += pixel
            if j == 3 or j == 4:
                pixels[1] += pixel
            if j == 5 or j == 6:
                pixels[2] += pixel
        min_pixels = int(shape[0]*shape[1]*threshold)
        # определяем сначала, есть ли жёлтый
        if pixels[0] >= min_pixels:
            calculated_color = "Red"
            series = 1
        if (pixels[1] >= min_pixels and calculated_color is None) or (calculated_color == "Red" and pixels[1] > pixels[0]):
            calculated_color = "Yellow"
            series = 2
        if pixels[2] >= min_pixels:
            calculated_color = "Green"
            series = 3
        
        if parameters["write_to_image"] and not calculated_color is None:
            cv2.putText(img, f"{calculated_color} #{parameters['traffic_light_number']}", (rectangle[0] - 120, (rectangle[1] + rectangle[3]) // 2 + 10),
            cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 0, 0), 1)

    frame_index = app_info["frame_index"]
    frame_rate = app_info["frame_rate"]

    if not frame_index is None and series != 0:
        return {'image': img, "additional_data": f"Номер светофора: {parameters['traffic_light_number']}, цвет: {calculated_color}", 
        "video_data": (frame_index/frame_rate, 1, series)}
    else:
        return {'image': img, "additional_data": f"Номер светофора: {parameters['traffic_light_number']}, цвет: {calculated_color}"}

if __name__ == "__main__":
    def get_boundaries_hsv(color_name):
        if color_name == "Фуксия":
            return (149, 205, 205), (151, 255, 255)
        if color_name == "Зелёный":
            return (71, 153, 82), (74, 173, 86)
        if color_name == "Красный":
            return (0, 153, 82), (1, 173, 86)

        if color_name == "red_traffic_light_before":
            return (177, 120, 190), (180, 180, 230)
        if color_name == "red_traffic_light_after":
            return (0, 120, 190), (10, 180, 230)
        if color_name == "yellow_traffic_light":
            return (22, 155, 219), (26, 240, 255)
        if color_name == "green_traffic_light":
            return (80, 155, 178), (83, 255, 217)

    colors = ("red_traffic_light_before", "red_traffic_light_after", "yellow_traffic_light", "green_traffic_light")
    img = cv2.imread(r'C:\ProgramData\cv_experiments\temp\5.bmp')

    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7), (3, 3))
    #element_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5), (3, 3))

    mask = cv2.inRange(hsv_img, (71, 141, 209), (74, 199, 235))

    output = cv2.bitwise_and(img, img, mask = mask)
    output = cv2.dilate(output, element)

    cv2.imshow(f"Output", output)

    gray_output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    contours, _ = cv2.findContours(gray_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    traffic_light_images = {}
    traffic_light_images_hsv = {}
    series = 0
    
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])
        if boundRect[i][2] > 1 and boundRect[i][3] > 1:
            traffic_light_images[i] = np.zeros((boundRect[i][3]+2, boundRect[i][2]-2, 3), np.uint8)
            traffic_light_images[i] = img[int(boundRect[i][1]+2):int(boundRect[i][1]+boundRect[i][3]-2), 
            int(boundRect[i][0]+2):int(boundRect[i][0]+boundRect[i][2]-2)]
            shape = traffic_light_images[i].shape
            traffic_light_images_hsv[i] = cv2.cvtColor(traffic_light_images[i], cv2.COLOR_BGR2HSV)
            cv2.imshow("Image {i}", traffic_light_images[i])
            pixels = [0, 0, 0] # красный, потом жёлитый, потом зелёный
            threshold = 0.015 # порог, при котором данный цвет вообще обнаруживается
            for j, color in enumerate(colors):
                pixel = np.count_nonzero(cv2.inRange(traffic_light_images_hsv[i], *get_boundaries_hsv(color)))
                if j == 0 or j == 1:
                    pixels[0] += pixel
                if j >= 2:
                    pixels[j-1] = pixel
            calculated_color = None
            min_pixels = int(shape[0]*shape[1]*threshold)
            # определяем сначала, есть ли жёлтый
            if pixels[0] >= min_pixels:
                calculated_color = "Red"
                series = 1
            if pixels[1] >= min_pixels:
                calculated_color = "Yellow"
                series = 2
            if pixels[2] >= min_pixels:
                calculated_color = "Green"
                series = 3
            
            if not calculated_color is None:
                cv2.putText(img, f"{calculated_color} #{1}", (200, 300),
                cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 0), 1)

    print(series)

    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print(edit_image(img, {"frame_rate": 30.0, "color": "Зелёный", "threshold": 0.015}, frame_index=5))

    cv2.waitKey(0)
    cv2.destroyAllWindows()