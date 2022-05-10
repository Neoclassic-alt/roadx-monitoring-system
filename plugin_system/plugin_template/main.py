import cv2
from plugin_system.common.data import *

# функция, если нужно загружать модель машинного обучения или другой объект
def load_heavy(parameters):
    return ...
    
# функция, непосредственно обрабатывающая изображение
def edit_image(img, parameters, **kwargs):
    return {'image': img, 'additional_data': ...}