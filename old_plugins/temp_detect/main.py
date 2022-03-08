import cv2

def edit_image(img, parameters, **kwargs):
    frame_index = kwargs.get("frame_index")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #edges = cv2.Canny(img, 200, 255, None, 3)
    _, dst1 = cv2.threshold(img, parameters['thresh'], 255, cv2.THRESH_BINARY_INV)
    #_, dst2 = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)
    #img = cv2.Sobel(img, cv2.CV_8U, 0, 1)
    M = cv2.getRotationMatrix2D(center=(img.shape[1] // 2, img.shape[0] // 2), 
    angle=parameters['angle'], scale=1)
    rotated = cv2.warpAffine(src=dst1, M=M, dsize=(img.shape[1], img.shape[0]))
    rotated_color = cv2.cvtColor(rotated, cv2.COLOR_GRAY2BGR)

    x1 = parameters['x1']
    x2 = parameters['x2']
    y1 = parameters['y1']
    y2 = parameters['y2']

    cv2.rectangle(rotated_color, (x1, y1), (x2, y2), (255, 0, 255), 1, cv2.LINE_8)

    area = rotated[y1:y2, x1:x2]

    #rotated[363:374, 300:360] = 255

    max_point = [0, 0]
    for y, row in enumerate(area):
        for x, col in enumerate(row):
            if col > 10 and x > max_point[0]:
                max_point = [x, y]

    max_point[0] += x1
    max_point[1] += y1

    cv2.circle(rotated_color, (max_point[0], max_point[1]), 3, (0, 0, 255), -1)
    if not frame_index is None:
        hours = ((kwargs["frame_index"]/2 + int(parameters['minutes'])) // 60 + int(parameters['hours'])) % 24
        minutes = (kwargs["frame_index"]/2 + int(parameters['minutes'])) % 60
        time = hours + minutes/100

        # первая точка в кортеже обозначает координату x или категорию столбца, 
        # вторая - координату y, третья - номер серии (от 1 до 3) (по умолчанию - 1)
        return {'image': rotated_color, 
        'additional_data': f"Координаты красной точки: ({max_point[0]}, {max_point[1]})", 
        'video_data': (time, (max_point[1] - 210.5)/7)}
    else:
        return {'image': rotated_color, 
        'additional_data': f"Координаты красной точки: ({max_point[0]}, {max_point[1]})"}