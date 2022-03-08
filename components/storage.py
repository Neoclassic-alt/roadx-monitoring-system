import numpy as np
import copy

class storage:
    plugins = None
    plugins_titles = []
    plugins_titles_to_names = {}
    plugins_settings = None # установленные настройки плагинов
    plugins_prior_settings = None # предварительные настройки плагинов
    opened_objects = [] # открытые объекты и плагины к ним (изображения, URLs)
    # с 24.12.2021 только объекты
    current_object = None # текущий открытый объект
    chain_of_plugins = [] # цепочка плагинов
    current_file_field_tag = {'item': None, 'var': None} # для сохранения имени файлового поля
    data_loads = [] # хранитель "тяжёлых" объектов. 
    # Формат: {'name': имя плагина, 'object': объект, 'need_load': нужна ли перезагрузка}
    additional_data = {} # дополнительная текстовая информация
    current_data = np.zeros(2000 * 2000 * 4)
    demo = True # если True, то функциональность ограничена
    is_dragging = False # перетаскивание методом Drag&Drop
    zoom = 100 # степень увеличения/уменьшения
    processed = False # для определения, был ли уже обработано изображение/файл
    crosshair = [False, None, None] # объект перекрестия. [0] - включен ли режим; [1] - кнопка; [2] - переменная плагина

    ### ДЛЯ ВИДЕО ###
    is_playing = False # воспроизводится ли видео
    current_frame = 0 # цифра текущего кадра видео
    frame_rate = 0 # количество кадров
    total_frames = 0 # общее число кадров
    video_data = {} # информация на графике о ролике
    ### ДЛЯ ВИДЕО: КОНЕЦ ###

    process_times = [] # информация о времени обработки данных
    # формат: [(время обработки плагином 1, время обработки плагином 2, ...), (время обработки плагином 1, время обработки плагином 2, ...), ...]

    program_settings = {"quality_of_pictures": 85, "auto_apply": False, "send_signal": True, 
    "display_image_process": True, "display_video_process": True}

    actions = []

    def write_action(func):
        def wrapper(*args):
            func(*args)
            if len(args) == 0:
                storage.actions.append({"function": func.__name__})
            if len(args) == 1:
                storage.actions.append({"function": func.__name__, "value": args[0]})
            if len(args) >= 2:
                storage.actions.append({"function": func.__name__, "key": args[0], "value": args[-1]})
        return wrapper

    @write_action
    def set_value(key, value):
        global storage
        if key == keys.PLUGINS:
            storage.plugins = value
        if key == keys.PLUGINS_TITLES:
            storage.plugins_titles = value
        if key == keys.PLUGINS_TITLES_TO_NAMES:
            storage.plugins_titles_to_names = value
        if key == keys.PLUGINS_SETTINGS:
            storage.plugins_settings = value
        if key == keys.PLUGINS_PRIOR_SETTINGS:
            storage.plugins_prior_settings = value
        if key == keys.OPENED_OBJECTS:
            storage.opened_objects = value
        if key == keys.CURRENT_OBJECT:
            storage.current_object = value
        if key == keys.CHAIN_OF_PLUGINS:
            storage.chain_of_plugins = value
        if key == keys.CURRENT_FILE_FIELD_TAG:
            storage.current_file_field_tag = value
        if key == keys.DATA_LOADS:
            storage.data_loads = value
        if key == keys.CURRENT_DATA:
            storage.current_data = value
        if key == keys.IS_PLAYING:
            storage.is_playing = value
        if key == keys.CURRENT_FRAME:
            storage.current_frame = value
        if key == keys.FRAME_RATE:
            storage.frame_rate = value
        if key == keys.TOTAL_FRAMES:
            storage.total_frames = value
        if key == keys.PROGRAM_SETTINGS:
            storage.program_settings = value
        if key == keys.DEMO:
            storage.demo = value
        if key == keys.ZOOM:
            storage.zoom = value
        if key == keys.PROCESSED:
            storage.processed = value
        if key == keys.CROSSHAIR:
            storage.crosshair = value

    @write_action
    def set_plugin_settings(key, value):
        storage.plugins_settings[key] = value

    @write_action
    def set_plugin_settings_field(key, field, value):
        storage.plugins_settings[key][field] = value

    @write_action
    def set_titles_to_names(key, value):
        storage.plugins_titles_to_names[key] = value
        storage.plugins_titles.append(key)

    @write_action
    def set_prior_plugin_settings(key, value):
        if len(key) == 2:
            storage.plugins_prior_settings[key[0]][key[1]] = value
        if len(key) == 1:
            storage.plugins_prior_settings[key[0]] = value

    @write_action
    def plugin_set_settings(name, new_settings):
        # new_settings - объект
        for key, value in new_settings.items():
            storage.plugins_settings[name][key] = value
            storage.plugins_prior_settings[name][key] = value

    @write_action
    def append_object(value):
        storage.opened_objects.append(value)

    @write_action
    def clear_opened_objects():
        storage.opened_objects.clear()

    @write_action
    def append_to_chain(title):
        storage.chain_of_plugins.append(title)

    @write_action
    def clear_chain():
        storage.chain_of_plugins.clear()

    @write_action
    def swap_plugins_in_chain(index, direction):
        if direction == "down":
            storage.chain_of_plugins[index], storage.chain_of_plugins[index + 1] = \
                storage.chain_of_plugins[index + 1], storage.chain_of_plugins[index]
        if direction == "up":
            storage.chain_of_plugins[index - 1], storage.chain_of_plugins[index] = \
                storage.chain_of_plugins[index], storage.chain_of_plugins[index - 1]

    @write_action
    def edit_need_load(plugin_name, value):
        index = list(map(lambda i: i['name'], storage.data_loads)).index(plugin_name)
        storage.data_loads[index]['need_load'] = value

    @write_action
    def new_data_load(plugin_name, object_):
        storage.data_loads.append({'name': plugin_name, 'object': object_, 'need_load': False})
        # все равно данные будут загружены, и значение 'need_load' пойдёт в False

    @write_action
    def add_additional_data(index, data):
        if storage.additional_data.get(index) is None:
            storage.additional_data[index] = []
        storage.additional_data[index].append(data)

    @write_action
    def clear_additional_data():
        storage.additional_data.clear()

    @write_action
    def add_video_data(data, plugin):
        if storage.video_data.get(plugin) is None:
            storage.video_data[plugin] = []
        storage.video_data[plugin].append(data)

    @write_action
    def clear_video_data():
        storage.video_data.clear()

    @write_action
    def add_time_data(data):
        storage.process_times.append(data)

    @write_action
    def clear_time_data():
        storage.process_times.clear()

    @write_action
    def toggle_playing():
        storage.is_playing = not storage.is_playing

    def next_current_frame():
        if storage.current_frame < storage.total_frames:
            storage.current_frame += 1
            return True
        return False

    def get_actions():
        return storage.actions

    @write_action
    def add_plugin(plugin, name, title, settings):
        # plugin - объект плагина
        storage.plugins[name] = plugin
        storage.plugins_titles.append(title)
        storage.plugins_titles_to_names[title] = name
        storage.plugins_settings[name] = copy.deepcopy(settings)
        storage.plugins_prior_settings[name] = copy.deepcopy(settings)

    @write_action
    def delete_plugin(plugin, name, title):
        # plugin - объект плагина
        del storage.plugins[name]
        del storage.plugins_titles[title]
        del storage.plugins_titles_to_names[title]
        del storage.plugins_settings[name]
        del storage.plugins_prior_settings[name]

class OBJECT_TYPES:
    image = "image"
    video = "video"
    stream = "stream"
    url = "url"
    file = "file" # video and image

class FILE_FORMATS:
    images = (".jpg", ".gif", ".jpeg", ".png")
    videos = (".avi", ".mp4", ".ogv", ".mpg", ".mov")
    all_objects = (*images, *videos)

class keys:
    PLUGINS = "plugins"
    PLUGINS_TITLES = "plugins_titles"
    PLUGINS_TITLES_TO_NAMES = "plugins_titles_to_names"
    PLUGINS_SETTINGS = "plugins_settings"
    PLUGINS_PRIOR_SETTINGS = "plugins_prior_settings"
    OPENED_OBJECTS = "opened_objects"
    CURRENT_OBJECT = "current_object"
    CHAIN_OF_PLUGINS = "chain_of_plugins"
    CURRENT_FILE_FIELD_TAG = "current_file_field_tag"
    DATA_LOADS = "data_loads"
    CURRENT_FRAME = "current_frame"
    TOTAL_FRAMES = "total_frames"
    FRAME_RATE = "frame_rate"
    IS_PLAYING = "is_playing"
    PROGRAM_SETTINGS = "program_settings"
    CURRENT_DATA = "current_data"
    DEMO = "demo"
    ZOOM = "zoom"
    PROCESSED = "processed"
    CROSSHAIR = "crosshair"