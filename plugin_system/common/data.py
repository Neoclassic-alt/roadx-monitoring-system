def get_yolo_model(model_size):
    if model_size == "nano":
        return "yolov5n"
    if model_size == "small":
        return "yolov5s"
    if model_size == "medium":
        return "yolov5m"
    if model_size == "big":
        return "yolov5l"
    if model_size == "extra":
        return "yolov5x"

def get_device(device_name):
    if device_name == "Процессор":
        return 'cpu'
    if device_name == "Видеокарта":
        return 'cuda'

def get_color(color_name): # работает в модели BGR
    if color_name == "Черный":
        return (0, 0, 0)
    if color_name == "Серый":
        return (128, 128, 128)
    if color_name == "Серебряный":
        return (192, 192, 192)
    if color_name == "Белый":
        return (255, 255, 255)
    if color_name == "Фуксия":
        return (255, 0, 255)
    if color_name == "Пурпурный":
        return (128, 0, 128)
    if color_name == "Синий":
        return (249, 51, 25)
    if color_name == "Красный":
        return (0, 0, 255)
    if color_name == "Малиновый":
        return (0, 0, 128)
    if color_name == "Жёлтый":
        return (0, 255, 255)
    if color_name == "Оливковый":
        return (0, 128, 128)
    if color_name == "Лайм":
        return (0, 255, 0)
    if color_name == "Зелёный":
        return (122, 233, 52)
    if color_name == "Бирюзовый":
        return (255, 255, 0)
    if color_name == "Кирпичный":
        return (0, 69, 255)
    if color_name == "Небесный":
        return (255, 191, 0)

# возврат значений в формате opencv-hsv
def get_boundaries_hsv(color_name):
    if color_name == "Фуксия":
        return (149, 205, 205), (151, 255, 255)
    if color_name == "Зелёный":
        return (71, 141, 209), (74, 199, 235)
    if color_name == "Красный":
        return (0, 153, 204), (1, 173, 220)

    if color_name == "red_traffic_light_before":
        return (174, 120, 73), (180, 255, 255)
    if color_name == "red_traffic_light_after_bright":
        return (0, 0, 180), (14, 80, 255)
    if color_name == "red_traffic_light_after_dark":
        return (0, 190, 0), (14, 255, 70)
    if color_name == "yellow_traffic_light_bright":
        return (22, 0, 180), (26, 80, 255)
    if color_name == "yellow_traffic_light_dark":
        return (22, 180, 0), (26, 255, 80)
    if color_name == "green_traffic_light_bright":
        return (80, 0, 165), (88, 80, 255)
    if color_name == "green_traffic_light_dark":
        return (80, 180, 0), (88, 255, 180)