import cv2
import numpy as np
from plugin_system.common.data import *
import json
   
# функция, непосредственно обрабатывающая изображение
def edit_image(img, parameters, app_info):
    points = np.array([parameters["point_one"], parameters["point_two"], parameters["point_three"], parameters["point_four"]], np.int32)
    points_reshaped = points.reshape((-1, 1, 2))
    if parameters["display"]:
        img = cv2.polylines(img, [points_reshaped], True, get_color(parameters['color']), parameters["thinkness"])
    if parameters["display"] and parameters["show_numbers"]:
        for i, point in enumerate(points):
            img = cv2.putText(img, f"{i+1}", (point[0] - 7, point[1] - 10), cv2.FONT_HERSHEY_DUPLEX, 0.75, get_color(parameters['color']))
    return {'image': img, 'additional_data': f"Точки многоугольника: {json.dumps(points.tolist())}"}