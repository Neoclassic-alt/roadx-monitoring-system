import dearpygui.dearpygui as dpg
import cv2
from threading import Thread
import components.photo_video as pv
from components.storage import storage
from components.storage import keys
from components.storage import OBJECT_TYPES, FILE_FORMATS, OBJECT_STATUSES
import components.custom_components as custom_components
import os
from queue import Queue
import time

class AppInfo():
    pass

results = []

# получить новые объекты
def open_objects(sender, app_data, user_data):
    if user_data == OBJECT_TYPES.file:
        selected = app_data['selections']
        for key, value in selected.items():
            short_url = value.rpartition("\\")[2]
            if value.endswith(FILE_FORMATS.images):
                storage.append_object({"url": value, "short_url": short_url, "type": OBJECT_TYPES.image, "status": OBJECT_STATUSES.new})
                custom_components.add_file_item(value, OBJECT_TYPES.image, short_url=short_url)
            if value.endswith(FILE_FORMATS.videos):
                storage.append_object({"url": value, "short_url": short_url, "type": OBJECT_TYPES.video, "status": OBJECT_STATUSES.new})
                custom_components.add_file_item(value, OBJECT_TYPES.video, short_url=short_url)

    if user_data == OBJECT_TYPES.url:
        urls = dpg.get_value('urls').split('\n')
        for url in urls:
            if url.rpartition('.')[-1] in FILE_FORMATS.images:
                storage.append_object({'url': url, 'type': OBJECT_TYPES.url})
            #if url.rpartition('.')[-1] in ("mp4", 'avi'):
            #    opened_objects.append({'url': url, 'type': functions.OBJECT_TYPES.stream, 'plugin': plugin})
        dpg.hide_item("add_urls_window")
        dpg.set_value("urls", "")
        dpg.set_value("apply_urls_plugin", "(Нет)")   
 
    if storage.current_object is None:
        storage.set_value(keys.CURRENT_OBJECT, storage.opened_objects[0])
        custom_components.set_file_current(storage.opened_objects[0]["url"])
        pv.open_cv(storage.current_object, activate=True)

    dpg.hide_item("hello_splash")
    dpg.show_item("group_of_objects")
    dpg.show_item("zoom")
    dpg.enable_item("prev_file_button")
    dpg.configure_item("prev_file_button", texture_tag="prev_file")
    dpg.enable_item("more_files_button")
    dpg.configure_item("more_files_button", texture_tag="more_files")
    dpg.enable_item("next_file_button")
    dpg.configure_item("next_file_button", texture_tag="next_file")
    dpg.enable_item("close_files_button")
    dpg.configure_item("close_files_button", texture_tag="close_image")

# открыть папку с файлами
def open_folder(sender, app_data):
    current_path = app_data['current_path']
    files = os.listdir(current_path)

    files_types = dpg.get_value("kinds_of_files")
    if files_types == "Изображения + Видео":
        file_filter = FILE_FORMATS.all_objects
    if files_types == "Изображения":
        file_filter = FILE_FORMATS.images
    if files_types == "Видео":
        file_filter = FILE_FORMATS.videos

    for file in files:
        if file.endswith(file_filter):
            if file.endswith(FILE_FORMATS.images):
                type_of_file = OBJECT_TYPES.image
            if file.endswith(FILE_FORMATS.videos):
                type_of_file = OBJECT_TYPES.video
            storage.append_object({"url": f"{current_path}\\{file}", "type": type_of_file})

    dpg.configure_item("combo_of_objects", items=tuple(map(lambda x: x['url'], storage.opened_objects)), 
    default_value=storage.opened_objects[0]['url'])

    dpg.show_item("group_of_objects")
    if storage.current_object is None:
        storage.set_value(keys.CURRENT_OBJECT, storage.opened_objects[0])
        pv.open_cv(storage.current_object)
    
# получить информацию по объекту из его url
def object_info(url):
    open_object = None
    for object_ in storage.opened_objects:
        if object_['url'] == url or object_['short_url'] == url:
            open_object = object_
            break
    return open_object

# сменить открытый объект в главном окне
def change_object(filename):
    custom_components.delete_file_current(storage.current_object["url"])
    storage.set_value(keys.CURRENT_OBJECT, object_info(filename))
    custom_components.set_file_current(storage.current_object["url"])
    pv.open_cv(storage.current_object)

def close_object(url=None):
    length = len(storage.opened_objects)
    if length == 0:
        return

    search_url = url or storage.current_object['url'] # если нет url из функции, 
    # значит, используется url текущего объекта

    if length == 1:
        storage.clear_opened_objects()
        dpg.delete_item("file_filter_container", children_only=True)
        dpg.hide_item("group_of_objects")
        dpg.hide_item("video_player")
        dpg.hide_item("close_and_delete_temp_files")
        dpg.hide_item("main_image_child_window")
        dpg.show_item("hello_splash")
        storage.set_value(keys.CURRENT_OBJECT, None)
        dpg.delete_item(f"file_{search_url}_handler")
        dpg.delete_item(f"file_{search_url}_move_handler")
        dpg.delete_item(dpg.get_item_parent(f"file_{search_url}"))
        dpg.disable_item("begin_processing_button")
    
    if length > 1:
        index_of_elem = tuple(map(lambda x: x['url'], storage.opened_objects)) \
        .index(search_url)
        
        storage.set_value(keys.OPENED_OBJECTS, 
            list(filter(lambda x: x['url'] != search_url, storage.opened_objects)))
        if len(storage.opened_objects) == index_of_elem:
            index_of_elem -= 1

        dpg.delete_item(f"file_{search_url}_handler")
        dpg.delete_item(f"file_{search_url}_move_handler")
        dpg.delete_item(dpg.get_item_parent(f"file_{search_url}"))
        if search_url == storage.current_object['url']:
            new_element = storage.opened_objects[index_of_elem]
            storage.set_value(keys.CURRENT_OBJECT, new_element)
            custom_components.set_file_current(new_element['url'])
            pv.open_cv(new_element)

def close_all_objects():
    if storage.current_object is None:
        return
    storage.clear_opened_objects()
    file_items = dpg.get_item_children("file_filter_container", slot=1)
    for item_group in file_items:
        file_item = dpg.get_item_children(item_group, slot=1)[0]
        tag = dpg.get_item_alias(file_item)
        dpg.delete_item(f"{tag}_handler")
        dpg.delete_item(f"{tag}_move_handler")
    dpg.delete_item("file_filter_container", children_only=True)
    dpg.hide_item("group_of_objects")
    storage.set_value(keys.CURRENT_OBJECT, None)
    dpg.hide_item("main_image_child_window")
    dpg.hide_item("video_player")
    dpg.show_item("hello_splash")
    dpg.disable_item("begin_processing_button")