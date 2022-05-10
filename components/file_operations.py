import dearpygui.dearpygui as dpg
import components.photo_video as pv
from components.storage import storage
from components.storage import keys
from components.storage import OBJECT_TYPES, FILE_FORMATS, OBJECT_STATUSES
import components.custom_components as custom_components
import components.interface_functions as inf
import os

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
            short_url = value.rpartition("\\")[2]
            if url.rpartition('.')[-1] in FILE_FORMATS.images:
                storage.append_object({'url': url, 'short_url': short_url, 'type': OBJECT_TYPES.url, "status": OBJECT_STATUSES.new})
                custom_components.add_file_item(url, OBJECT_TYPES.url, short_url=short_url)
        dpg.hide_item("add_urls_window")
        dpg.set_value("urls", "")

    if user_data == OBJECT_TYPES.stream:
        type_of_camera = dpg.get_value("type_of_camera")
        if type_of_camera == "Веб-камера":
            number_of_camera = dpg.get_value("camera_number")
            storage.append_object({'url': int(number_of_camera), 'short_url': f"Камера {number_of_camera}", 
            'type': OBJECT_TYPES.stream, "status": OBJECT_STATUSES.new})
            custom_components.add_file_item(number_of_camera, OBJECT_TYPES.stream, short_url=f"Камера {number_of_camera}")
        if type_of_camera == "IP-камера":
            camera_url, camera_user, camera_password = dpg.get_values(["camera_url", "camera_user", "camera_password"])
            if camera_user != "" and camera_password != "":
                url = camera_url.replace("rtsp://", "")
                url = f"rtsp://{camera_user}:{camera_password}@{url}"
            else:
                url = camera_url
            storage.append_object({'url': url, 'short_url': f"Камера {camera_url}", 'type': OBJECT_TYPES.stream, 
            "status": OBJECT_STATUSES.new})
            custom_components.add_file_item(url, OBJECT_TYPES.stream, short_url=camera_url)
 
    if storage.current_object is None:
        storage.set_value(keys.CURRENT_OBJECT, storage.opened_objects[0])
        custom_components.set_file_current(storage.opened_objects[0]["url"])
        pv.open_cv(storage.current_object, activate=True)
        dpg.enable_item("change_after_connect_to_camera")

    inf.show_tool_panel()

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
                storage.append_object({"url": f"{current_path}\\{file}", "short_url": file, "type": 
                OBJECT_TYPES.image, "status": OBJECT_STATUSES.new})
                custom_components.add_file_item(f"{current_path}\\{file}", OBJECT_TYPES.image, short_url=file)
            if file.endswith(FILE_FORMATS.videos):
                storage.append_object({"url": f"{current_path}\\{file}", "short_url": file, "type": 
                OBJECT_TYPES.video, "status": OBJECT_STATUSES.new})
                custom_components.add_file_item(f"{current_path}\\{file}", OBJECT_TYPES.video, short_url=file)

    if storage.current_object is None:
        storage.set_value(keys.CURRENT_OBJECT, storage.opened_objects[0])
        custom_components.set_file_current(storage.opened_objects[0]["url"])
        pv.open_cv(storage.current_object, activate=True)

    inf.show_tool_panel()
    
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
        dpg.disable_item("change_after_connect_to_camera")
    
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
    dpg.disable_item("change_after_connect_to_camera")