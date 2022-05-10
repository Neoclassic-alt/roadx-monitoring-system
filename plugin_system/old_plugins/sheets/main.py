import cv2

def edit_image(img, parameters, app_info):
    linesGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    linesGray = cv2.Canny(img, 50, 255, None, 3)
    linesGray = cv2.dilate(linesGray, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    if parameters['invert']:
        linesGray = 255 - linesGray

    return {"image": linesGray, "format": "gray"}