import cv2
import numpy as np
from plugin_system.common.data import *
import re
import json
from plugin_system.common.functions import intersect_detecting

# функция, непосредственно обрабатывающая изображение
def edit_image(img, parameters, app_info):
    additional_data = app_info["additional_data"]
    cars = [x for x in additional_data if x['plugin'].startswith('Распознавание машин')]
    car_crossings = [x for x in additional_data if x['plugin'].startswith('Контур пешеходного перехода')]
    roads = [x for x in additional_data if x['plugin'].startswith('Контур дороги')]
    traffic_lights_colors = [x for x in additional_data if x['plugin'].startswith('Информация о цвете светофора')]

    cars_coordinates = []
    pedestrian_crossings_coordinates = []
    roads_coordinates = []
    traffic_light_color = [0, None]
    ## координаты людей
    cars = cars[0]['text'].split('\n')
    for car in cars:
        groups = re.match(r'Левая верхняя точка: \((\d+), (\d+)\), правая нижняя точка: \((\d+), (\d+)\)', car)
        if not groups is None:
            groups = groups.groups()
            cars_coordinates.append((int(groups[0]), int(groups[1]), int(groups[2]), int(groups[3])))
    
    ## координаты пешеходных переходов
    for crossing in car_crossings:
        pedestrian_crossings_coordinates.append(json.loads(crossing['text'].replace('Точки многоугольника: ', '')))
    
    ## координаты дорог
    for road in roads:
        roads_coordinates.append(json.loads(road['text'].replace('Точки многоугольника: ', '')))

    ## цвет светофора
    traffic_light_color_text = traffic_lights_colors[0]['text']
    match = re.match(r'Номер светофора: (\d+), цвет: (.+)', traffic_light_color_text)
    if not match is None:
        match = match.groups()
        traffic_light_color[0] = int(match[0])
        traffic_light_color[1] = match[1]

    # нарушает правила (violate), соблюдает правила (observe), не определено (undefined)
    car_statuses = []

    # График stem
    # Если обнаружено несколько пешеходов, то красная серия с количеством пешеходов
    # Если светофор не горит, то "не определено" (со значением 1). Цвет синий
    # Если нет нарушений, то зелёный (со значением 1).
    
    for car in cars_coordinates:
        new_car_bottom_points = [[0, 0], [0, 0], [0, 0], [0, 0]]
        # нижняя четверть
        car_up_bottom = car[1] + int((car[3] - car[1]) * 3 // 4)
        # с левой верхней по часовой стрелке
        new_car_bottom_points[0] = [car[0], car_up_bottom]
        new_car_bottom_points[1] = [car[2], car_up_bottom]
        new_car_bottom_points[2] = [car[2], car[3]]
        new_car_bottom_points[3] = [car[0], car[3]]
        #points_numpy = np.array(new_car_bottom_points, np.int32)
        #points_reshaped = points_numpy.reshape((-1, 1, 2))
        #img = cv2.polylines(img, [points_reshaped], True, get_color("Серебряный"), 2)
        if traffic_light_color[1] == "Green":
            car_statuses.append("observe")
        if traffic_light_color[1] == "None":
            car_statuses.append("observe")

        if traffic_light_color[1] == "Yellow" or traffic_light_color[1] == "Red":
            if intersect_detecting(new_car_bottom_points, pedestrian_crossings_coordinates):
                car_statuses.append("violate")
    
    if app_info['type'] == 'video' and app_info['mode'] == 'all':
        frame_index = app_info["frame_index"]
        frame_rate = app_info["frame_rate"]
        if len(car_statuses) > 0 and car_statuses[0] == 'undefined':
            return {'image': img, 'additional_data': f'Нельзя определить нарушения ПДД', 'video_data': (frame_index/frame_rate, 1, 2)}
        elif len(car_statuses) == 0 or car_statuses[0] != 'undefined':
            observe_count = car_statuses.count('observe')
            violate_count = car_statuses.count('violate')
            series = 3
            count = 1
            if violate_count > 0:
                series = 1
                count = violate_count
            return {'image': img, 'additional_data': f'Соблюдают правила дорожного движения {observe_count} машин, нарущают правила {violate_count} машин',
            'video_data': (frame_index/frame_rate, count, series), 'violation': violate_count > 0}

    if app_info['type'] == 'image' or app_info['mode'] == 'one':
        if len(car_statuses) > 0 and car_statuses[0] == 'undefined':
            return {'image': img, 'additional_data': f'Нельзя определить нарушения ПДД'}
        elif len(car_statuses) == 0 or car_statuses[0] != 'undefined':
            observe_count = car_statuses.count('observe')
            violate_count = car_statuses.count('violate')
            series = 3
            count = 1
            if violate_count > 0:
                series = 1
                count = violate_count
            return {'image': img, 'additional_data': f'Соблюдают правила дорожного движения {observe_count} машин, нарущают правила {violate_count} машин'}