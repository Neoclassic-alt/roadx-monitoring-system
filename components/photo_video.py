import dearpygui.dearpygui as dpg
import cv2
import numpy as np
from components.storage import OBJECT_STATUSES, storage
from components.storage import keys
import components.plugin_manager as pm
import components.file_operations as fo
import components.interface_functions as inf
import components.custom_components as cc
import zlib
import os
import shutil
import requests
import beepy
import time

TEMP_FRAMES_FOLDER = r"C:/ProgramData/cv_experiments/temp_frames"
TEMP_PROCESSING_FRAMES_FOLDER = r"C:/ProgramData/cv_experiments/temp_processed_frames"

class OBJECT_TYPES:
    image = "image"
    video = "video"
    stream = "stream"
    url = "url"
    file = "file" # video and image

class FILE_FORMATS:
    images = (".jpg", ".gif", ".jpeg", ".png")
    videos = (".avi", ".mp4", ".ogv")
    all_objects = (*images, *videos)

# действия при нажатии кнопки play
def toggle_play():
    if storage.is_playing:
        dpg.configure_item("play_button", texture_tag="play")
    else:
        dpg.configure_item("play_button", texture_tag="pause")
    storage.toggle_playing()

def set_play(state):
    if state:
        dpg.configure_item("play_button", texture_tag="pause")
    else:
        dpg.configure_item("play_button", texture_tag="play")
    storage.set_value(keys.IS_PLAYING, state)

def get_temp_folder_name(url):
    return zlib.crc32(url.encode('utf-8'), 0)

def process_image(data, single_image=True, index=None):
    """Пояснения к параметрам:
    data - изображение OpenCV
    single_image - режим обработки: одно изображение или все кадры
    index - индекс обрабатываемого фрейма"""
    if single_image and not storage.all_frames:
        if len(storage.chain_of_plugins) == 1:
            dpg.set_value("text_of_loading", "Применение плагина...")
        elif len(storage.chain_of_plugins) > 1:
            dpg.set_value("text_of_loading", "Применение плагинов...")
    process_times = []
    for plugin_title in storage.chain_of_plugins:
        plugin = storage.plugins_titles_to_names[plugin_title.rpartition('##')[0]]
        heavy = None
        parameters = storage.plugins_settings.get(plugin_title)
        if parameters['need_load']:
            dpg.hide_item("progress_bar")
            dpg.hide_item("time_evaluation")
            storage.set_value(keys.IS_DIVISIBLE, False)
            storage.process_timer_to_zero()
            heavy = pm.load_heavy(plugin, parameters["settings"], single_image)
            storage.edit_need_load(plugin_title, heavy)
        else:
            heavy = parameters["payload"]

        dpg.show_item("progress_bar")
        dpg.hide_item("loading_indicator")
        dpg.show_item("state_of_loading")
        dpg.show_item("time_evaluation")
        storage.set_value(keys.IS_DIVISIBLE, True)

        mode = "all"
        if not storage.all_frames:
            mode = "one"
        app_info = {"heavy": heavy, "frame_rate": storage.frame_rate, "frame_index": index, 
        'type': storage.current_object['type'], 'mode': mode}
        start = time.perf_counter()

        if not index is None and not storage.additional_data.get(index) is None and len(storage.additional_data[index]) >= 1:
            app_info["additional_data"] = storage.additional_data[index]
            dpg.hide_item("no_image_data_text")
            dpg.show_item("image_index_slider_group")
        if index is None and not storage.additional_data.get(0) is None and len(storage.additional_data[0]) >= 1:
            app_info["additional_data"] = storage.additional_data[0]
            dpg.hide_item("no_image_data_text")
        apply = storage.plugins[plugin]['transform']
        ready = None
        ready = apply(data, parameters["settings"], app_info)
        data = ready['image']
        if not ready.get('additional_data') is None and not index is None:
            storage.add_additional_data(index, {'text': ready['additional_data'], 'plugin': plugin_title})
        if not ready.get('additional_data') is None and index is None:
            storage.add_additional_data(0, {'text': ready['additional_data'], 'plugin': plugin_title})
        if not ready.get('video_data') is None:
            storage.add_video_data(ready['video_data'], plugin_title)
        if not ready.get('violation') is None and ready['violation']:
            storage.add_violation(index, plugin_title)
        end = time.perf_counter()
        process_times.append(end - start)
    storage.add_time_data(process_times)
    return data

# открыть новые объекты при помощи OpenCV
def open_cv(object, activate=False):
    data = None
    url = object["url"]
    object_type = object["type"]
    #dpg.hide_item("limit_1_minute")
    storage.clear_additional_data()
    #storage.set_value(keys.PROCESSED, False)
    storage.set_value(keys.IS_CAMERA_PLAYING, False)
    if object_type == OBJECT_TYPES.image:
        data = cv2.imread(url)
    if object_type == OBJECT_TYPES.url:
        data = get_image_from_url(url)
        if data is None:
            print("Объект недоступен") # TODO: поменять на другой текст ошибки
            return
    if object_type in (OBJECT_TYPES.image, OBJECT_TYPES.url):
        if len(storage.chain_of_plugins) > 0:
            data = process_image(data)
        change_texture(data)
        #dpg.delete_item("additional_text_group", children_only=True)
        dpg.hide_item("state_of_loading")
        dpg.show_item("status_bar_info")
        dpg.hide_item("video_player_window")
        dpg.hide_item("close_and_delete_temp_files")
        dpg.disable_item("close_and_delete_temp_files")
        if activate:
            cc.enable_menu_item("save_image_menu_item")
            cc.enable_menu_item("save_all_images_menu_item")
        #show_additional_data()
    if object_type in OBJECT_TYPES.video:
        # CRC-код будет именем папки с временными файлами
        temp_folder_name = zlib.crc32(url.encode('utf-8'), 0)
        # открываем видео при помощи OpenCV
        cap = cv2.VideoCapture(url)
        length_of_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        #if (length_of_video / frame_rate) > 60 and storage.demo:
        #    dpg.show_item("limit_1_minute")
        #    dpg.hide_item("state_of_loading")
        #    return
        storage.set_value(keys.FRAME_RATE, frame_rate)
        temp_frames_folder = r"C:/ProgramData/cv_experiments/temp_frames"
        if not os.path.isdir(temp_frames_folder):
            os.mkdir(temp_frames_folder)
        temp_folder_path = rf"{temp_frames_folder}/{temp_folder_name}"
        if not os.path.isdir(temp_folder_path):
            storage.set_value(keys.IS_PROCESSING, True)
            storage.set_value(keys.IS_DIVISIBLE, True)
            dpg.show_item("state_of_loading")
            dpg.hide_item("loading_indicator")
            dpg.show_item("progress_bar")
            dpg.hide_item("status_bar_info")
            os.mkdir(temp_folder_path)

            count_of_frames = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imwrite(f"{temp_folder_path}/{count_of_frames}.jpg", frame, (cv2.IMWRITE_JPEG_QUALITY, 
                storage.program_settings["quality_of_pictures"]))
                count_of_frames += 1
                dpg.set_value("text_of_loading", f"Открытие видео")
                dpg.set_value("progress_bar", count_of_frames / length_of_video)
                storage.set_value(keys.PART_OF_PROCESS, count_of_frames / length_of_video)
            cap.release()
            if storage.program_settings["send_signal"]:
                beepy.beep(sound='ready')

        storage.set_value(keys.CURRENT_FRAME, 0)

        count_of_frames = len(os.listdir(temp_folder_path))
        storage.set_value(keys.TOTAL_FRAMES, count_of_frames)
        dpg.configure_item("image_index_slider", max_value=storage.total_frames)
        dpg.set_value("time_video_from_begin", "0:00")
        seconds = storage.total_frames // storage.frame_rate
        minutes = seconds // 60
        seconds = seconds % 60
        dpg.set_value("video_duration", "{0:02d}:{1:02d}".format(minutes, seconds))
        data = cv2.imread(f"{temp_folder_path}/{storage.current_frame}.jpg")
        change_texture(data)
        inf.resize_viewport()

        dpg.hide_item("state_of_loading")
        dpg.hide_item("progress_bar")
        storage.process_is_finished()
        dpg.show_item("video_player_window")
        dpg.show_item("close_and_delete_temp_files")
        dpg.enable_item("close_and_delete_temp_files")
        if activate:
            cc.enable_menu_item("save_image_menu_item")
            cc.enable_menu_item("save_all_frames_menu_item")
            cc.enable_menu_item("save_video_menu_item")

    if object_type == OBJECT_TYPES.stream:
        cap = cv2.VideoCapture(url)
        storage.set_value(keys.CAPTION, cap)
        storage.set_value(keys.IS_CAMERA_PLAYING, True)

    dpg.show_item("main_image_child_window")
    if activate:
        cc.enable_menu_item("close_menu_item")
        cc.enable_menu_item("close_all_menu_item")
        count_of_links = len(dpg.get_item_children("plugin_node_editor", slot=0))
        count_of_nodes = len(dpg.get_item_children("plugin_node_editor", slot=1))
        if count_of_links == count_of_nodes - 1:
            dpg.enable_item("begin_processing_button")
    dpg.enable_item("expand_modes_button")
    dpg.hide_item("expand_tooltip")
    if object_type != OBJECT_TYPES.stream:
        inf.update_status_bar_info()
        inf.update_viewport_title()
    dpg.show_item("status_bar_info")

# загрузить изображение с Интернета
def get_image_from_url(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        response = response.raw
        data = np.asarray(bytearray(response.read()), dtype="uint8")
        data = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return data
    else:
        return None

# отобразить добавочную информацию
def show_additional_data(frame_index=0):
    # 0 применяется, если открыто изображение
    if len(storage.additional_data) != 0:
        dpg.show_item("additional_text")
        for text in storage.additional_data[frame_index]:
            dpg.add_collapsing_header(label='Информация от плагина ' + text['plugin'], 
            parent="additional_text_group", closable=True)
            dpg.add_text(text['text'], parent=dpg.last_item(), indent=20)
    else:
        dpg.hide_item("additional_text")

# открыть кадр из видео (без плагинов или с плагинами, если обработка по одному)
def open_frame(frame_index):
    url = storage.current_object["url"]
    storage.set_value(keys.CURRENT_FRAME, frame_index)
    dpg.set_item_width("player_progress", frame_index / (storage.total_frames - 1) * dpg.get_item_width("player_pan"))
    if frame_index == 0:
        dpg.hide_item("player_progress")
    else:
        dpg.show_item("player_progress")

    temp_folder_name = get_temp_folder_name(url)
    temp_frames_folder = TEMP_FRAMES_FOLDER
    if len(storage.chain_of_plugins) and storage.all_frames and \
    storage.current_object["status"] == OBJECT_STATUSES.actual:
        temp_frames_folder = TEMP_PROCESSING_FRAMES_FOLDER
    temp_folder_path = rf"{temp_frames_folder}/{temp_folder_name}"

    if frame_index == storage.total_frames - 1:
        set_play(False)

    data = cv2.imread(f"{temp_folder_path}/{storage.current_frame}.jpg")

    #if not dpg.get_value("apply_to_all_frames"):
    #    storage.clear_additional_data()
    #dpg.delete_item("additional_text_group", children_only=True)

    if len(storage.chain_of_plugins) and not storage.all_frames:
        data = process_image(data)
        dpg.hide_item("state_of_loading")

    #if storage.is_playing:
    #    dpg.hide_item("additional_text")
    #else:
    #    dpg.configure_item("additional_text", label="Результаты обработки кадра при помощи плагинов")
    #    if storage.program_settings["display_image_process"] and dpg.get_value("apply_to_all_frames"):
    #        show_additional_data(frame_index)
    #    if storage.program_settings["display_image_process"] and not dpg.get_value("apply_to_all_frames"):
    #        show_additional_data()
        
    shape = data.shape
    data = cv2.cvtColor(data, cv2.COLOR_BGR2RGBA)
    data = data.flatten() / 255
    storage.current_data[0:(shape[0] * shape[1] * 4)] = data
    seconds = storage.current_frame // storage.frame_rate
    minutes = seconds // 60
    seconds = seconds % 60
    dpg.set_value("time_video_from_begin", "{0:02d}:{1:02d}".format(minutes, seconds))

# обработать плагинами все кадры из видео
def process_all_frames():
    url = storage.current_object["url"]
    temp_folder_name = get_temp_folder_name(url)
    temp_folder_path = rf"{TEMP_FRAMES_FOLDER}/{temp_folder_name}"
    temp_folder_processing_path = rf"{TEMP_PROCESSING_FRAMES_FOLDER}/{temp_folder_name}"

    if not os.path.isdir(TEMP_PROCESSING_FRAMES_FOLDER):
        os.mkdir(TEMP_PROCESSING_FRAMES_FOLDER)
    if not os.path.isdir(temp_folder_processing_path):
        os.mkdir(temp_folder_processing_path)

    dpg.show_item("state_of_loading")
    dpg.hide_item("loading_indicator")
    storage.set_value(keys.IS_PROCESSING, True)
    storage.set_value(keys.IS_DIVISIBLE, True)
    if len(storage.chain_of_plugins) == 1:
        dpg.set_value("text_of_loading", "Применение плагина к кадрам")
    if len(storage.chain_of_plugins) > 1:
        dpg.set_value("text_of_loading", "Применение плагинов к кадрам")

    storage.clear_video_data()
    storage.clear_time_data()
    storage.clear_violations()

    for i in range(storage.total_frames):
        data = cv2.imread(f"{temp_folder_path}/{i}.jpg") # чтение из основной папки
        data = process_image(data, i == storage.current_frame, index=i)
        cv2.imwrite(f"{temp_folder_processing_path}/{i}.jpg", data, (cv2.IMWRITE_JPEG_QUALITY, 
        storage.program_settings["quality_of_pictures"])) # запись в дополнительную папку
        dpg.set_value("progress_bar", i / storage.total_frames)
        storage.set_value(keys.PART_OF_PROCESS, i / storage.total_frames)

    dpg.hide_item("state_of_loading")
    storage.process_is_finished()

    dpg.delete_item("video_plots_group", children_only=True)
    dpg.configure_item("plots_combo", items=["(Нет)"])

    if storage.program_settings["display_video_process"] and len(storage.video_data) > 0:
        inf.create_plots()
        cc.enable_button("information_button", "information_button_text")
        dpg.hide_item("no_plots_text")
        dpg.show_item("red_point_image")
        dpg.set_item_width("information_button", 124)
        dpg.show_item("plot_combo_group")
        dpg.show_item("plots_combo")
    else:
        dpg.show_item("no_plots_text")
        dpg.hide_item("plot_combo_group")
        dpg.show_item("plots_combo")

    inf.show_image_data_frame(None, 0)
    inf.show_violations()
    
    if storage.program_settings["send_signal"]:
        beepy.beep(sound='ready')

def go_to_begin():
    storage.set_value(keys.CURRENT_FRAME, 0)
    open_frame(0)

def go_to_end():
    storage.set_value(keys.CURRENT_FRAME, storage.total_frames - 1)
    open_frame(storage.total_frames - 1)
    set_play(False)

def go_to_prev_frame():
    if storage.current_frame > 0:
        storage.set_value(keys.CURRENT_FRAME, storage.current_frame - 1)
    open_frame(storage.current_frame)

def go_to_next_frame():
    if storage.current_frame < storage.total_frames:
        storage.set_value(keys.CURRENT_FRAME, storage.current_frame + 1)
    open_frame(storage.current_frame)

def delete_temp_folders():
    url = storage.current_object["url"]
    temp_folder_name = get_temp_folder_name(url)
    temp_frames_folder = r"C:/ProgramData/cv_experiments/temp_frames"
    temp_frames_processed_folder = r"C:/ProgramData/cv_experiments/temp_processed_frames"
    temp_folder_path = rf"{temp_frames_folder}/{temp_folder_name}"
    temp_folder_processed_path = rf"{temp_frames_processed_folder}/{temp_folder_name}"
    # удаляем всю папку вместе с содержимым
    shutil.rmtree(temp_folder_path)
    if os.path.isdir(temp_folder_processed_path):
        shutil.rmtree(temp_folder_processed_path)

def delete_temp_folders_and_close_video():
    if storage.is_playing:
        storage.set_value(keys.IS_PLAYING, False)
    delete_temp_folders()
    fo.close_object()

def change_texture(data):
    shape = data.shape
    zoom = storage.zoom
    data = cv2.cvtColor(data, cv2.COLOR_BGR2RGBA)
    data = data.flatten() / 255
    data = np.asarray(data, np.float32)

    dpg.delete_item("main_image_desk") # удаление изображения
    dpg.delete_item("main_image") # удаление текстуры
    #dpg.delete_item("image_mouse_tooltip") # удаление подсказки

    storage.set_value(keys.CURRENT_DATA, data)

    dpg.add_raw_texture(shape[1], shape[0], storage.current_data, format=dpg.mvFormat_Float_rgba, 
    tag="main_image", parent="texture_registry") # создание текстуры
    dpg.add_image("main_image", width=shape[1]*zoom//100, height=shape[0]*zoom//100, tag="main_image_desk",
    parent="main_image_child_window") # наложение изображения на текстуру

def zoom(direction):
    values = [25, 33, 50, 75, 90, 100, 125, 150, 200, 300, 400]
    index = values.index(storage.zoom)
    if direction == "plus":
        dpg.enable_item("minus_zoom_button")
        dpg.configure_item("minus_zoom_button", texture_tag="zoom_minus")
        if index != len(values):
            storage.set_value(keys.ZOOM, values[index+1])
        if index == len(values) - 2:
            dpg.disable_item("plus_zoom_button")
            dpg.configure_item("plus_zoom_button", texture_tag="zoom_plus_inactive")
    if direction == "minus":
        dpg.enable_item("plus_zoom_button")
        dpg.configure_item("plus_zoom_button", texture_tag="zoom_plus")
        if index != 0:
            storage.set_value(keys.ZOOM, values[index-1])
        if index == 1:
            dpg.disable_item("minus_zoom_button")
            dpg.configure_item("minus_zoom_button", texture_tag="zoom_minus_inactive")
    if direction == "100":
        dpg.enable_item("plus_zoom_button")
        dpg.configure_item("plus_zoom_button", texture_tag="zoom_plus")
        dpg.enable_item("minus_zoom_button")
        dpg.configure_item("minus_zoom_button", texture_tag="zoom_minus")
        storage.set_value(keys.ZOOM, 100)
    width = dpg.get_item_width("main_image")
    height = dpg.get_item_height("main_image")
    dpg.configure_item("main_image_desk", width=width*storage.zoom//100, height=height*storage.zoom//100)
    dpg.configure_item("100_zoom_button", label=f"{storage.zoom}%")
