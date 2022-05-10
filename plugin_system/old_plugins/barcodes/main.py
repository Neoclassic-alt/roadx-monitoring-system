import cv2
import numpy as np
import math

def initial_module():
    return ({'title': 'Размер штрихкода', 'type': 'slider', 'var': 'size',
    'default_value': 1, 'settings': {'min': 1, 'max': 3, 'int': True}},
    {'title': 'Выделять линии при помощи преобразования Хафа', 'type': 'checkbox', 'var': 'check_lines'},
    {'title': 'Коэффицент rho', 'type': 'numbers', 'var': 'rho', 'default_value': 1},
    {'title': 'Коэффицент theta (выражается как pi / введённое значение)', 'type': 'numbers', 'var': 'theta', 'default_value': 180},
    {'title': 'Порог', 'type': 'number', 'var': 'threshold', 'default_value': 150},
    {'title': 'В качестве структурного элемента использовать:', 'type': 'combo', 
    'var': 'morph_form', 'settings': ("Прямоугольник", "Круг", "Крест")})

def edit_image(img, parameters, **kwargs):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.Canny(gray, 220, 255, None, 3)

    morph_form = None
    if parameters['morph_form'] == "Прямоугольник":
        morph_form = cv2.MORPH_RECT

    if parameters['morph_form'] == "Круг":
        morph_form = cv2.MORPH_ELLIPSE

    if parameters['morph_form'] == "Крест":
        morph_form = cv2.MORPH_CROSS

    kernel_dilate = cv2.getStructuringElement(morph_form, (5 + 4*(parameters['size'] - 1), 5 + 4*(parameters['size'] - 1)))
    kernel_erode = cv2.getStructuringElement(morph_form, (3 + 2*(parameters['size'] - 1), 3 + 2*(parameters['size'] - 1)))

    gradient = cv2.dilate(gray, kernel_dilate)
    gradient = cv2.dilate(gray, kernel_erode)

    # contours
    contours, hierarchy = cv2.findContours(gradient, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contoursArea = []
    # нужно выбрать наибольший элемент
    for i in range(len(contours)):
        contoursArea.append(cv2.contourArea(contours[i]))

    maxIndex = 0
    maxSize = 0

    for i in range(len(contoursArea)):
        if contoursArea[i] > maxSize:
            maxSize = contoursArea[i]
            maxIndex = i

    color = (0, 0, 240)
    if (len(contours) > 0):
        rect = cv2.minAreaRect(contours[maxIndex])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(img, [box], 0, color, 2)

    if parameters['check_lines']:
        lines = cv2.HoughLines(gray, parameters['rho'], np.pi / parameters['theta'], parameters['threshold'], None, 0, 0)

        if lines is not None:
            for i in range(0, len(lines)):
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a * rho
                y0 = b * rho
                pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
                pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
                cv2.line(img, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)

    return {'image': img}