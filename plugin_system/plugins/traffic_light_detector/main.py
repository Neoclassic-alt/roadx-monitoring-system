import cv2
import torch
from plugin_system.common.data import *

def load_heavy(parameters):
    model_name = get_yolo_model(parameters['size'])
    device = get_device(parameters['device'])
    model = torch.hub.load('ultralytics/yolov5', model_name, device=device, 
    force_reload=parameters['force_reload'])
    return model
    
def edit_image(img, parameters, app_info):
    color = get_color(parameters['color'])

    results = app_info['heavy'](img)

    tensors = results.xyxy[0]
    # только светофоры
    tensors = tensors[tensors[:, 5] == 9]
    additional_text = ''
    for tensor in tensors:
        if tensor[4].item() >= parameters['threshold']:
            if parameters['display']:
                cv2.rectangle(img, (int(tensor[0].item())-2, int(tensor[1].item())+2), 
        (int(tensor[2].item())-2, int(tensor[3].item())+2), color, parameters['thinkness'])

            additional_text += f'Левая верхняя точка: ({int(tensor[0].item())}, {int(tensor[1].item())}), ' + \
            f'правая нижняя точка: ({int(tensor[2].item())}, {int(tensor[3].item())}), вероятность: ' + \
                str(round(tensor[4].item(), 6)) + '\n'

    return {'image': img, 'additional_data': additional_text}