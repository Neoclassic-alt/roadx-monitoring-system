import cv2
import numpy as np
from common.data import *
import re
import json
from common.functions import intersect_detecting

# функция, непосредственно обрабатывающая изображение
def edit_image(img, parameters, app_info):
    additional_data = app_info["additional_data"]
    persons = [x for x in additional_data if x['plugin'] == 'Распознавание людей']
    pedestrian_crossings = [x for x in additional_data if x['plugin'].startswith('Контур пешеходного перехода')]
    roads = [x for x in additional_data if x['plugin'].startswith('Контур дороги')]
    traffic_lights_colors = [x for x in additional_data if x['plugin'] == 'Информация о цвете светофора']

    persons_coordinates = []
    pedestrian_crossings_coordinates = []
    roads_coordinates = []
    traffic_light_color = [0, None]
    ## координаты людей
    persons = persons[0]['text'].split('\n')
    for person in persons:
        groups = re.match(r'Левая верхняя точка: \((\d+), (\d+)\), правая нижняя точка: \((\d+), (\d+)\)', person)
        if not groups is None:
            groups = groups.groups()
            persons_coordinates.append((int(groups[0]), int(groups[1]), int(groups[2]), int(groups[3])))
    
    ## координаты пешеходных переходов
    for crossing in pedestrian_crossings:
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
    pedestrian_statuses = []

    # График stem
    # Если обнаружено несколько пешеходов, то красная серия с количеством пешеходов
    # Если светофор не горит, то "не определено" (со значением 1). Цвет синий
    # Если нет нарушений, то зелёный (со значением 1).
    
    for pedestrian in persons_coordinates:
        new_pedestrian_bottom_points = [[0, 0], [0, 0], [0, 0], [0, 0]]
        # нижняя четверть
        pedestrian_up_bottom = pedestrian[1] + int((pedestrian[3] - pedestrian[1]) * 3 // 4)
        # с левой верхней по часовой стрелке
        new_pedestrian_bottom_points[0] = [pedestrian[0], pedestrian_up_bottom]
        new_pedestrian_bottom_points[1] = [pedestrian[2], pedestrian_up_bottom]
        new_pedestrian_bottom_points[2] = [pedestrian[2], pedestrian[3]]
        new_pedestrian_bottom_points[3] = [pedestrian[0], pedestrian[3]]
        #points_numpy = np.array(new_pedestrian_bottom_points, np.int32)
        #points_reshaped = points_numpy.reshape((-1, 1, 2))
        #img = cv2.polylines(img, [points_reshaped], True, get_color("Серебряный"), 2)
        if traffic_light_color[1] == "Red":
            observe = intersect_detecting(new_pedestrian_bottom_points, pedestrian_crossings_coordinates)
            if not observe: # пересечений пешехода с местностью не обнаружено
                violate = intersect_detecting(new_pedestrian_bottom_points, roads_coordinates)
                if violate:
                    pedestrian_statuses.append("violate")
            else:
                pedestrian_statuses.append("observe")
        if traffic_light_color[1] == "None":
            violate = intersect_detecting(new_pedestrian_bottom_points, roads_coordinates)
            if violate:
                pedestrian_statuses.append("violate")
            else:
                pedestrian_statuses.append("undefined")

        if traffic_light_color[1] == "Yellow" or traffic_light_color[1] == "Green":
            if intersect_detecting(new_pedestrian_bottom_points, pedestrian_crossings_coordinates):
                pedestrian_statuses.append("violate")
                continue
            if intersect_detecting(new_pedestrian_bottom_points, roads_coordinates):
                pedestrian_statuses.append("violate")
                continue
    
    if app_info['type'] == 'video':
        frame_index = app_info["frame_index"]
        frame_rate = app_info["frame_rate"]
        if len(pedestrian_statuses) > 0 and pedestrian_statuses[0] == 'undefined':
            return {'image': img, 'additional_data': f'Нельзя определить нарушения ПДД', 'video_data': (frame_index/frame_rate, 1, 2)}
        elif len(pedestrian_statuses) == 0 or pedestrian_statuses[0] != 'undefined':
            observe_count = pedestrian_statuses.count('observe')
            violate_count = pedestrian_statuses.count('violate')
            series = 3
            count = 1
            if violate_count > 0:
                series = 1
                count = violate_count
            return {'image': img, 'additional_data': f'Соблюдают правила дорожного движения {observe_count} пешеходов, нарущают правила {violate_count} пешеходов',
            'video_data': (frame_index/frame_rate, count, series)}

    if app_info['type'] == 'image':
        if len(pedestrian_statuses) > 0 and pedestrian_statuses[0] == 'undefined':
            return {'image': img, 'additional_data': f'Нельзя определить нарушения ПДД'}
        elif len(pedestrian_statuses) == 0 or pedestrian_statuses[0] != 'undefined':
            observe_count = pedestrian_statuses.count('observe')
            violate_count = pedestrian_statuses.count('violate')
            series = 3
            count = 1
            if violate_count > 0:
                series = 1
                count = violate_count
            return {'image': img, 'additional_data': f'Соблюдают правила дорожного движения {observe_count} пешеходов, нарущают правила {violate_count} пешеходов'}