import cv2
import numpy as np

def initial_module():
    return ({'title': 'Путь к шаблону', 'type': 'file', 'var': 'template', 'settings': {'required': True}},
    {'title': 'Путь к маске', 'type': 'file', 'var': 'mask'},
    {'title': 'Снизить разрешение', 'type': 'checkbox', 'var': 'resize'},
    {'title': 'Метод обнаружения шаблона', 'type': 'combo', 'var': 'method',
    'settings': ("TM_SQDIFF", "TM_SQDIFF_NORMED", "TM_CCORR", "TM_CCORR_NORMED", 
    "TM_CCOEFF", "TM_CCOEFF_NORMED"), "default_value": "TM_SQDIFF_NORMED"},)

def edit_image(img, parameters, **kwargs):
    print("Дошло до функции edit_image: template_match")
    print(parameters)
    template = cv2.imread(parameters['template'])
    if parameters['mask']:
        mask = cv2.imread(parameters['mask'])
    if parameters['resize']:
        img = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))
        template = cv2.resize(template, (template.shape[1] // 2, template.shape[0] // 2))
        mask = cv2.resize(mask, (mask.shape[1] // 2, mask.shape[0] // 2))

    result = cv2.matchTemplate(img, template, cv2.TM_SQDIFF_NORMED, mask=mask)

    cv2.normalize( result, result, 0, 255, cv2.NORM_MINMAX, -1)

    result = result.astype(np.uint8)
    _, result = cv2.threshold(result, 30, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    result = cv2.dilate(result, kernel)

    contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i in range(len(contours)):
        color = (0, 0, 255)
        cv2.drawContours(img, contours, i, color, 2, cv2.LINE_8, hierarchy, 0, (template.shape[0] // 2, template.shape[1] // 2))

    return {'image': img, 'additional_data': f"Обнаружено {len(contours)} шаблонов"}

    # методы обнаружения совпадений (https://docs.opencv.org/4.5.3/de/da9/tutorial_template_matching.html)
    # шаблон
    # маска