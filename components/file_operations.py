import dearpygui.dearpygui as dpg
import cv2
from threading import Thread
import components.photo_video as pv
from components.storage import storage
from components.storage import keys
from components.storage import OBJECT_TYPES, FILE_FORMATS, OBJECT_STATUSES
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
            if value.endswith(FILE_FORMATS.images):
                storage.append_object({"url": value, "type": OBJECT_TYPES.image, "status": OBJECT_STATUSES.new})
            if value.endswith(FILE_FORMATS.videos):
                storage.append_object({"url": value, "type": OBJECT_TYPES.video, "status": OBJECT_STATUSES.new})

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
        pv.open_cv(**storage.current_object) # <- вот функция, где мы должны пойти дальше

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
        pv.open_cv(**storage.current_object)
    
# получить информацию по объекту из его url
def object_info(url):
    open_object = None
    for object_ in storage.opened_objects:
        if object_['url'] == url:
            open_object = object_
            break
    return open_object

# сменить открытый объект в главном окне
def change_object(sender, app_data, user_data):
    storage.set_value(keys.CURRENT_OBJECT, object_info(app_data))
    pv.open_cv(**storage.current_object)

# сохранение объектов
def save_all_files(sender, app_data):
    common_info = {
        "file_path": app_data['file_path_name'],
        "image_format": dpg.get_value("image_format"),
        "video_format": dpg.get_value("video_format"),
        "set_program_name": dpg.get_value("set_program_name"),
        "program_name": dpg.get_value("program_name")
        #"save_without_plugin": dpg.get_value("save_without_plugin")
    }
    number_of_threads = dpg.get_value("number_of_threads")
    queue = Queue() # создаём очередь обработки
    
    # Запускаем потом и очередь
    for i in range(number_of_threads):
        t = FileSaver(i + 1, queue, storage.plugins, storage.plugins_settings, common_info)
        t.setDaemon(True)
        t.start()
    
    # Даем очереди нужные нам ссылки для скачивания
    for i, object_ in enumerate(storage.opened_objects):
        queue.put({**object_, 'i': i})

    # удаление обработанных файлов
    if dpg.get_value("close_all_files"):
        #AppInfo.opened_objects.clear()
        storage.clear_opened_objects()
        #AppInfo.current_object = None
        storage.set_value(keys.CURRENT_OBJECT, None)
        dpg.configure_item("combo_of_objects", items=())
        dpg.delete_item("main_image")
        dpg.delete_item("main_image_desk")
        dpg.hide_item("group_of_objects")

class FileSaver(Thread):
    def __init__(thread_number, queue, plugins, plugins_settings, common_info):
        Thread.__init__()
        AppInfo.thread_number = thread_number
        AppInfo.queue = queue
        AppInfo.common_info = common_info
        AppInfo.plugins = plugins
        AppInfo.plugins_settings = plugins_settings

        AppInfo.start_time = None

    def run():
        while True:
            # Получаем url из очереди
            object_ = AppInfo.queue.get()

            AppInfo.start_time = time.perf_counter_ns()

            # Сохраняем файл
            AppInfo.save_file(object_, **AppInfo.common_info)
            
            # Отправляем сигнал о том, что задача завершена
            AppInfo.queue.task_done()

    # сохраняет один объект
    def save_file(object_, file_path, image_format = 'png', video_format = 'mp4', 
    set_program_name = False, program_name = None):
        if object_['type'] == OBJECT_TYPES.image:
            if set_program_name == "Исходные имена":
                filename = file_path + '\\' + object_['url'].rpartition('\\')[-1].rpartition('.')[0] + '.' + image_format
            if set_program_name == "Программное имя":
                if program_name.find('$'):
                    filename = file_path + '\\' + program_name.replace('$', str(object_['i'] + 1)) + '.' + image_format
                else:
                    return
            AppInfo.save_cv(object_['url'], OBJECT_TYPES.image, filename, object_['plugin'])
        if object_['type'] == OBJECT_TYPES.url:
            if set_program_name == "Исходные имена":
                filename = file_path + '\\' + object_['url'].rpartition('/')[-1].rpartition('.')[0] + '.' + image_format
            if set_program_name == "Программное имя":
                if program_name.find('$'):
                    filename = file_path + '\\' + program_name.replace('$', str(object_['i'] + 1)) + '.' + image_format
                else:
                    return
            AppInfo.save_cv(object_['url'], OBJECT_TYPES.url, filename, object_['plugin'])

        # сохранить объект при помощи OpenCV
    def save_cv(url, type, filename, plugin = None):
        data = None
        if type == storage.OBJECT_TYPES.image:
            data = cv2.imread(url)
        if type == storage.OBJECT_TYPES.url:
            data = AppInfo.get_image_from_url(url)
        if len(storage.chain_of_plugins) > 0:
            data = AppInfo.process_image(data)
        cv2.imwrite(filename, data, (cv2.IMWRITE_JPEG_QUALITY, storage.program_settings["quality_of_pictures"]))
        end_time = time.perf_counter_ns()
        
        results.append([AppInfo.thread_number, filename, plugin, AppInfo.start_time, end_time, end_time - AppInfo.start_time])


def close_object():
    length = len(storage.opened_objects)
    if length == 0:
        return

    if length == 1:
        storage.clear_opened_objects()
        dpg.configure_item("combo_of_objects", items=[])
        dpg.hide_item("group_of_objects")
        dpg.hide_item("video_player")
        dpg.hide_item("close_and_delete_temp_files")
        dpg.hide_item("main_image_child_window")
        storage.set_value(keys.CURRENT_OBJECT, None)
    
    if length > 1:
        index_of_elem = tuple(map(lambda x: x['url'], storage.opened_objects)) \
        .index(storage.current_object['url'])
        
        storage.set_value(keys.OPENED_OBJECTS, 
            list(filter(lambda x: x['url'] != storage.current_object['url'], storage.opened_objects)))
        if len(storage.opened_objects) == index_of_elem:
            index_of_elem -= 1

        dpg.configure_item("combo_of_objects", items=tuple(map(lambda x: x['url'], storage.opened_objects)),
            default_value=storage.opened_objects[index_of_elem]['url'])
        storage.set_value(keys.CURRENT_OBJECT, storage.opened_objects[index_of_elem])
        pv.open_cv(**storage.opened_objects[index_of_elem])

def close_all_objects():
    if storage.current_object is None:
        return
    storage.clear_opened_objects()
    dpg.configure_item("combo_of_objects", items=[])
    dpg.hide_item("group_of_objects")
    storage.set_value(keys.CURRENT_OBJECT, None)
    dpg.hide_item("main_image_child_window")