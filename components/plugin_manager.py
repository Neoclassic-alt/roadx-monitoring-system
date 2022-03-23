import dearpygui.dearpygui as dpg
import components.utils as utils
import components.photo_video as pv
from components.storage import storage
from components.storage import keys
from components.storage import OBJECT_TYPES
import os
import json
import importlib
import components.styling as themes
import random

def load_plugins():
    all_folders = os.listdir('.\plugins')
    plugins = {}
    for f8ile in all_folders:
        module_files = os.listdir(f'plugins/{f8ile}')
        is_plugin = True
        try:
            if not ('info.json' in module_files) or not f'main.py' in module_files:
                raise FileNotFoundError("В модуле нет файлов main.py и/или info.json")
        except Exception as e:
            print(e)
            is_plugin = False
        if is_plugin:
            plugins[f8ile] = {'info': '', 'interface': '', 'payload': None, 'transform': '', 'group': None}
            with open(f"plugins/{f8ile}/info.json", "r", encoding='utf-8') as json_file:
                plugins[f8ile]['info'] = json.load(json_file)
            # импорт плагина
            module = importlib.import_module(f'plugins.{f8ile}.main')
            if os.path.isfile(f"plugins/{f8ile}/interface.json"):
                with open(f"plugins/{f8ile}/interface.json", "r", encoding='utf-8') as interface_file:
                    plugins[f8ile]['interface'] = json.load(interface_file)
            else:
                plugins[f8ile]['interface'] = None
            plugins[f8ile]['transform'] = module.edit_image # обратите внимание, что функция не вызывается
            if not plugins[f8ile]['info'].get('heavy') is None: # содержит ли "полезную нагрузку"
                plugins[f8ile]['payload'] = module.load_heavy
    return plugins

def set_titles_to_names():
    for key in list(storage.plugins.keys()):
        storage.set_titles_to_names(storage.plugins[key]['info']['title'], key)

def set_prior_plugin_settings(sender, app_data, user_data):
    current_plugin = storage.plugins_titles_to_names[dpg.get_value("list_of_plugins")]
    storage.set_prior_plugin_settings([current_plugin, user_data], app_data)

def set_plugin_settings(sender, app_data, user_data):
    current_plugin = storage.plugins_titles_to_names[dpg.get_value("list_of_plugins")]
    storage.set_plugin_settings(current_plugin, storage.plugins_prior_settings[current_plugin])
    with open('C:\ProgramData\cv_experiments\settings.json', 'w') as write_file:
        json.dump(storage.plugins_settings, write_file, indent=4, ensure_ascii=True)
    dpg.show_item("settings_have_saved_text" + user_data)
    # обновление настроек
    if not storage.current_object is None:
        if storage.current_object['type'] == OBJECT_TYPES.image:
            pv.open_cv(**storage.current_object)
        if storage.current_object['type'] == OBJECT_TYPES.video:
            pv.open_frame(storage.current_frame)

# выдать меню с информацией о плагине
def more_plugin_info(sender):
    current_plugin = storage.plugins_titles_to_names[dpg.get_value("list_of_plugins")]
    info = storage.plugins[current_plugin]['info']
    with dpg.window(label="Подробности о плагине", width=300, height=300, popup=True, 
    pos=(dpg.get_mouse_pos(local=False)[0], dpg.get_mouse_pos(local=False)[1])):
        dpg.add_text(info['title'])
        dpg.bind_item_font(dpg.last_item(), font="title")
        dpg.add_text("Автор: " + info['author'] + '\n')
        if not info.get('description') is None:
            dpg.add_text(info['description'])
        dpg.add_text("Версия: " + info['version'])
        if info.get('display') and 'additional_data' in info['display']:
            dpg.add_text("Плагин отображает дополнительную информацию", color=(127, 77, 226))
        if info.get('display') and 'video_data' in info['display']:
            dpg.add_text("Плагин отображает график при обработке видео", color=(52, 233, 122))

# создать меню с настройками плагина
def open_plugin_settings(sender):
    plugin_title = dpg.get_value("list_of_plugins")
    current_plugin = storage.plugins_titles_to_names[plugin_title]
    interface = storage.plugins[current_plugin].get('interface')
    plugin_settings = storage.plugins_settings[current_plugin]
    if interface is None:
        return
    random_num = random.randint(0, 100500)
    window_title = f"Настройки плагина «{plugin_title}»"
    if len(plugin_title) > 25:
        window_title = "Настройки плагина «" + plugin_title[:22] + "...»"
        if plugin_title.find("#") != -1:
            window_title = "Настройки плагина «" + plugin_title.rpartition(' #')[0][:23] + "... #" + \
            plugin_title.rpartition(' #')[2] + "»" 
    with dpg.window(label=window_title, autosize=True, pos=(300, 50), max_size=(-1, 600), user_data=random_num,
    on_close=on_close, no_resize=True):
        
        for field in interface:
            if field['type'] != 'checkbox':
                with dpg.group(horizontal=True, horizontal_spacing=3):
                    dpg.add_text(field['title']) # заголовок
                    if field['type'] != 'combo' and field.get('settings') \
                    and field['settings'].get('required'):
                        dpg.add_text("*", color=(255, 0, 0, 255))
                    if not field.get('description') is None:
                        dpg.add_spacer()
                        dpg.add_image("help_img")
                        dpg.add_tooltip(dpg.last_item())
                        dpg.add_text(field['description'], parent=dpg.last_item())

            default_value = plugin_settings.get(field['var'])
            multiline = False
            settings = {'min_value': 1, 'max_value': 999, 'int': False}

            # если необходима перезагрузка тяжёлого объекта
            def set_prior_settings_with_reload(sender, app_data, user_data):
                set_prior_plugin_settings(sender, app_data, user_data)
                need_loads_data = [x for x in storage.data_loads if x["name"] == current_plugin]
                if len(need_loads_data) != 0:
                    storage.edit_need_load(current_plugin, True)

            callback = set_prior_plugin_settings
            if field.get('heavy_reload'): # перезагрузка тяжёлого объекта
                callback = set_prior_settings_with_reload

            if field['type'] == "input":
                if not field.get('settings') is None:
                    if not field['settings'].get('multiline') is None:
                        multiline = field['settings']['multiline']
                dpg.add_input_text(default_value=default_value, multiline=multiline, 
                callback=callback, user_data=field['var'], width=400)

            if field['type'] == "file":
                with dpg.add_group(horizontal=True):
                    dpg.add_input_text(default_value="", readonly=True, width=300)
                    dpg.add_button(label="Добавить файл", callback=lambda: set_file_field(dpg.last_item(), field['var']))

            if field['type'] == 'slider':
                if not field.get('settings') is None:
                    if not field['settings'].get('min') is None:
                        settings['min_value'] = field['settings']['min']
                    if not field['settings'].get('max') is None:
                        settings['max_value'] = field['settings']['max']
                    if not field['settings'].get('int') is None:
                        settings['int'] = field['settings']['int']
                if settings['int']:
                    dpg.add_slider_int(min_value=settings['min_value'], max_value=settings['max_value'], 
                    default_value=default_value, callback=callback, user_data=field['var'], width=400)
                else:
                    dpg.add_slider_float(min_value=settings['min_value'], max_value=settings['max_value'], 
                    default_value=default_value, callback=callback, user_data=field['var'], width=400)

            if field['type'] == '2d-point':
                # задание двух слайдеров от x до y
                def set_prior_settings_to_point(sender, app_data, user_data):
                    current_plugin = storage.plugins_titles_to_names[dpg.get_value("list_of_plugins")]
                    get_point = plugin_settings.get(user_data[1])
                    if get_point is None:
                        get_point = [0, 0]
                    if user_data[0] == 'x':
                        get_point[0] = app_data
                    if user_data[0] == 'y':
                        get_point[1] = app_data
                    storage.set_prior_plugin_settings([current_plugin, user_data[1]], get_point)
                settings = {"x_min": 0, "x_max": 640, "y_min": 0, "y_max": 480}
                if not field.get("settings") is None:
                    settings["x_min"] = field["settings"].get("x_min") or 0
                    settings["x_max"] = field["settings"].get("x_max") or 640
                    settings["y_min"] = field["settings"].get("y_min") or 0
                    settings["y_max"] = field["settings"].get("y_max") or 480

                if default_value is None:
                    default_value = [0, 0]

                with dpg.group(horizontal=True):
                    crosshair = False
                    width = 195
                    if field.get('settings') is None or field['settings'].get('crosshair') is None or field['settings']['crosshair']:
                        crosshair = True
                        width = 176
                    dpg.add_input_int(min_value=settings["x_min"], max_value=settings["x_max"], 
                    default_value=default_value[0], callback=set_prior_settings_to_point, user_data=['x', field['var']]
                    , width=width, min_clamped=True, max_clamped=True, step=0)
                    dpg.add_input_int(min_value=settings["y_min"], max_value=settings["y_max"], 
                    default_value=default_value[1], callback=set_prior_settings_to_point, user_data=['y', field['var']]
                    , width=width, min_clamped=True, max_clamped=True, step=0)
                    if crosshair:
                        button = dpg.add_image_button("crosshair_img", width=16, height=16, callback=set_crosshair_mode, user_data=field['var'])
                        dpg.bind_item_theme(dpg.last_item(), themes.get_crosshair_button_theme())
                        with dpg.tooltip(button):
                            dpg.add_text("Наведите на изображение и нажмите в нужном месте")

            if field['type'] == 'checkbox':
                if not field.get('description') is None:
                    with dpg.group(horizontal=True, horizontal_spacing=5):
                        dpg.add_checkbox(label=field['title'], default_value=default_value or False, callback=callback, 
                user_data=field['var'])
                        dpg.add_image("help_img")
                        dpg.add_tooltip(dpg.last_item())
                        dpg.add_text(field['description'], parent=dpg.last_item())
                else:
                    dpg.add_checkbox(label=field['title'], default_value=default_value or False, callback=callback, 
                user_data=field['var'])

            if field['type'] == 'combo':
                dpg.add_combo(items=field['settings'], callback=callback, user_data=field['var'], 
                default_value=default_value or field['settings'][0], width=400)

            if field['type'] == 'number':
                if not field.get('settings') is None:
                    if not field['settings'].get('min') is None:
                        settings['min_value'] = field['settings']['min']
                    if not field['settings'].get('max') is None:
                        settings['max_value'] = field['settings']['max']
                    if not field['settings'].get('int') is None:
                        settings['int'] = field['settings']['int']
                if settings['int']:
                    dpg.add_input_int(default_value=default_value, callback=callback, user_data=field['var'],
                    min_value=settings['min_value'], max_value=settings['max_value'], width=400)
                else:
                    dpg.add_input_float(default_value=default_value or 0, callback=callback, user_data=field['var'],
                    min_value=settings['min_value'], max_value=settings['max_value'], width=400)

            dpg.add_spacer(height=6)
        with dpg.group(horizontal=True):    
            dpg.add_button(label="Сохранить настройки", callback=set_plugin_settings, user_data=str(random_num))
            dpg.add_text("Настройки сохранены", color=(152, 79, 234), show=False, tag="settings_have_saved_text" + str(random_num))

def duplicate_plugin(sender=None, app_data=None, user_data=None, title=None):
    selected_plugin = None
    if title is None:
        selected_plugin = dpg.get_value("list_of_plugins")
    else:
        selected_plugin = title
    plugin_name = storage.plugins_titles_to_names[selected_plugin]
    plugin = storage.plugins[plugin_name].copy()
    list_of_plugins = dpg.get_item_configuration("list_of_plugins")['items']
    # вычислим внешнее название плагина без #
    clean_name = selected_plugin
    if selected_plugin.find('#') != -1:
        clean_name = selected_plugin.rpartition(' #')[0]
    duplicated_plugins = list(filter(lambda title: title.startswith(clean_name), list_of_plugins))
    new_title = clean_name + f' #{len(duplicated_plugins) + 1}'
    list_of_plugins.append(new_title)
    dpg.configure_item("list_of_plugins", items=list_of_plugins)
    new_plugin_name = plugin_name + f'#{len(duplicated_plugins) + 1}'
    plugin_settings = storage.plugins_settings[plugin_name].copy()
    storage.add_plugin(plugin, new_plugin_name, new_title, plugin_settings)
    return new_plugin_name, new_title

def set_file_field(item, var):
    storage.current_file_field_tag['item'] = item
    storage.current_file_field_tag['var'] = var
    dpg.show_item("pc_file_plugin_dialog")

# специальная функция для полей с путями файлов
def file_set_path(sender, app_data):
    selection = list(app_data['selections'].values())
    dpg.set_value(storage.current_file_field_tag['item'], selection[0])
    set_prior_plugin_settings(None, selection[0], storage.current_file_field_tag['var'])

def open_plugins_window():
    dpg.show_item("plugins_window")

def apply_chain():
    if storage.current_object['type'] in (OBJECT_TYPES.image, OBJECT_TYPES.url):
        pv.open_cv(**storage.current_object)
    if storage.current_object['type'] == OBJECT_TYPES.video:
        if dpg.get_value("apply_to_all_frames"):
            pv.process_all_frames()
        pv.open_frame(storage.current_frame)
    storage.set_value(keys.PROCESSED, True)

# загрузка "тяжёлых" данных
def load_heavy(plugin, parameters, single_image=True):
    need_load = False
    filtered_load = list(filter(lambda x: x['name'] == plugin, storage.data_loads))
    if len(filtered_load) == 0:
        need_load = True
    if len(filtered_load) == 1 and filtered_load[0]['need_load']:
        storage.edit_need_load(plugin, False)
        need_load = True
    # загрузим данные
    if need_load:
        dpg.show_item("state_of_loading")
        dpg.set_value("text_of_loading", "Загрузка плагина...")
        heavy = storage.plugins[plugin]['payload'](parameters)
        if len(filtered_load) == 0:
            storage.new_data_load(plugin, heavy)
        #dpg.hide_item("state_of_loading")
        if not single_image or storage.current_frame == 0:
            if len(storage.chain_of_plugins) == 1:
                dpg.set_value("text_of_loading", "Применение плагина к кадрам")
            if len(storage.chain_of_plugins) > 1:
                dpg.set_value("text_of_loading", "Применение плагинов к кадрам")
        return heavy
    else:
        return filtered_load[0]['object']

def process_chain(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        current_text = ''
        if not len(storage.chain_of_plugins):
            dpg.set_value("chain_of_plugins", "Нет плагинов")
        else:
            for item in storage.chain_of_plugins:
                current_text += item + '  →  '
            current_text = current_text.rpartition('  →  ')[0]
            if len(current_text) > 91:
                current_text = current_text[:80] + '...' + f" (всего {len(storage.chain_of_plugins)}" + \
            f" {utils.plural(len(storage.chain_of_plugins), 'плагин', 'плагина', 'плагинов')})"
            dpg.set_value("chain_of_plugins", current_text)
        if not storage.current_object is None and storage.program_settings["auto_apply"]:
            apply_chain()
    return wrapper

@process_chain
def add_to_chain(sender=None, app_data=None, user_data=None, title=None):
    if title is None:
        plugin_title = dpg.get_value("list_of_plugins")
    else:
        plugin_title = title
    list_of_plugins = dpg.get_item_configuration("plugins_in_chain")['items']
    if len(storage.chain_of_plugins) >= 5 and storage.demo: # ограничение по числу плагинов в цепочке
        dpg.show_item("limit_5_plugins")
        return
    else:
        dpg.hide_item("limit_5_plugins")
    if plugin_title in list_of_plugins:
        return
    storage.append_to_chain(plugin_title)
    dpg.configure_item("plugins_in_chain", items=storage.chain_of_plugins)
    dpg.enable_item("delete_from_chain_of_plugins_button")
    if len(list_of_plugins) == 1:
        dpg.enable_item("swap_up_button")
        dpg.enable_item("swap_down_button")
    dpg.disable_item("add_to_chain_of_plugins")
   
@process_chain
def delete_from_chain():
    plugin_title = dpg.get_value("plugins_in_chain")
    if plugin_title:
        storage.set_value(keys.CHAIN_OF_PLUGINS, 
        list(filter(lambda x: x != plugin_title, storage.chain_of_plugins)))
        dpg.configure_item("plugins_in_chain", items=storage.chain_of_plugins)
    if not storage.current_object is None:
        pv.open_cv(**storage.current_object)
    if len(storage.chain_of_plugins) != 0:
        dpg.configure_item("plugins_in_chain", default_value=storage.chain_of_plugins[0])
    check_plugin(None, dpg.get_value("list_of_plugins"), None)

@process_chain
def swap(direction):
    plugin_title = dpg.get_value("plugins_in_chain")
    if plugin_title and len(storage.chain_of_plugins) > 0:
        index = storage.chain_of_plugins.index(plugin_title)
        if direction == "down" and index != len(storage.chain_of_plugins) - 1:
            storage.swap_plugins_in_chain(index, "down")
            dpg.configure_item("plugins_in_chain", items=storage.chain_of_plugins)
        if direction == "up" and index != 0:
            storage.swap_plugins_in_chain(index, "up")
            dpg.configure_item("plugins_in_chain", items=storage.chain_of_plugins)

# проверка плагина при нажатии на него в списке плагинов
def check_plugin(sender, app_data, user_data):
    show_previous(sender, app_data, user_data)
    set_enable_delete_button(sender, app_data, user_data)
    check_exist_in_chain(sender, app_data, user_data)
    ## Check have interface
    plugin_name = storage.plugins_titles_to_names[app_data]
    plugin = storage.plugins[plugin_name]
    if plugin['interface'] is None:
        dpg.disable_item("open_settings_button")
    else:
        dpg.enable_item("open_settings_button")

# Необходимо показать текст с предшествующими плагинами, если таковые есть
def show_previous(sender, app_data, user_data):
    plugin_name = storage.plugins_titles_to_names[app_data]
    plugin = storage.plugins[plugin_name]
    previous_list = plugin['info'].get("previous")
    titles_of_previous_plugins = []
    titles_of_missing_plugins = []
    if not previous_list is None:
        dpg.show_item("previous_warning_plugin")
        for previous in previous_list:
            title_of_plugin = storage.plugins[previous]['info'].get('title')
            if not title_of_plugin is None:
                titles_of_previous_plugins.append(storage.plugins[previous]['info']['title'])
            else:
                titles_of_previous_plugins.append(previous)
        for title in titles_of_previous_plugins:
            clean_title = title
            if title.find('#') != -1:
                clean_title = title.rpartition(' #')[0]
            if not clean_title in storage.chain_of_plugins:
                titles_of_missing_plugins.append(clean_title)
        if len(titles_of_missing_plugins):
            dpg.delete_item("previous_warning_tooltip", children_only=True)
            for title in titles_of_missing_plugins:
                dpg.add_text(title, color=(255, 0, 0), bullet=True, parent="previous_warning_tooltip")
            dpg.hide_item("previous_plugins_state")
        else:
            dpg.delete_item("previous_warning_tooltip", children_only=True)
            dpg.show_item("previous_plugins_state")
    else:
        dpg.hide_item("previous_warning_plugin")

# делаем кнопку активной, если плагин дублирован
def set_enable_delete_button(sender, app_data, user_data):
    selected_plugin = app_data
    if selected_plugin.find('#') != -1:
        dpg.enable_item("delete_from_plugins_list_button")
    else:
        dpg.disable_item("delete_from_plugins_list_button")

def check_exist_in_chain(sender, app_data, user_data):
    if app_data in storage.chain_of_plugins:
        dpg.disable_item("add_to_chain_of_plugins")
    else:
        dpg.enable_item("add_to_chain_of_plugins")

def open_chain_from_file(sender, app_data, user_data):
    file_path = app_data["file_path_name"]
    with open(file_path, "r", encoding="utf-8") as json_file:
        chain = json.load(json_file)
    storage.clear_chain()
    dpg.configure_item("plugins_in_chain", items=[])

    ### Процесс преобразования инструкций в конкретный результат
    for instruction in chain:
        plugin_title = storage.plugins[instruction["name"]]['info']['title']
        plugin_name = instruction["name"]
        if not instruction.get("duplicate") is None and instruction["duplicate"]:
            plugin_name, plugin_title = duplicate_plugin(title=plugin_title)
        add_to_chain(title=plugin_title)
        ## копирование настроек
        if not instruction.get("settings") is None:
            storage.plugin_set_settings(plugin_name, instruction["settings"])

# триггер при закрытии окна
def on_close(sender, app_data, user_data):
    dpg.delete_item("settings_have_saved_text" + str(user_data))
    if storage.crosshair[0]:
        dpg.delete_item("image_mouse_tooltip")
        #dpg.bind_item_handler_registry("main_image_desk", "none_handler")
        dpg.hide_item("image_handler_registry")
        storage.set_value(keys.CROSSHAIR, [False, None, None])

def drag_plugin():
    if storage.is_dragging == False:
        mouse_pos = dpg.get_mouse_pos(local=False)
        item_pos = dpg.get_item_pos("plugins_window")
        relative = (mouse_pos[0] - item_pos[0], mouse_pos[1] - item_pos[1])
        item = dpg.get_item_configuration("list_of_plugins")['items'][int((relative[1] - 73) // 20)]
        dpg.set_value("drag_text", item)
        dpg.configure_item("drop_plugin", drag_data=item)
        storage.is_dragging = True

def undragging():
    storage.is_dragging = False

# позволяет при нажатии на плагин в цепочке плагинов изменять выбор в списке плагинов
def set_plugin_in_list(sender, app_data, user_data):
    dpg.set_value("list_of_plugins", app_data)
    check_plugin(sender, app_data, user_data)

def get_mouse_pos():
    mouse_pos = dpg.get_mouse_pos(local=False)
    window_pos = dpg.get_item_pos("main_image_child_window")
    y_scroll = dpg.get_y_scroll("objects_window")
    x_scroll = dpg.get_x_scroll("main_image_child_window")
    dpg.set_value("image_mouse_tooltip_text", f"({int(mouse_pos[0] - window_pos[0] + x_scroll)}, \
{int(mouse_pos[1] - window_pos[1] + y_scroll)})")

# функция при нажатии на картинку в crosshair_mode 
def set_2d_point_values():
    mouse_pos = dpg.get_mouse_pos(local=False)
    window_pos = dpg.get_item_pos("main_image_child_window")
    y_scroll = dpg.get_y_scroll("objects_window")
    x_scroll = dpg.get_x_scroll("main_image_child_window")
    #dpg.bind_item_handler_registry("main_image_desk", "none_handler")
    dpg.hide_item("image_handler_registry")
    dpg.bind_item_theme(storage.crosshair[1], themes.get_crosshair_button_theme())
    current_plugin = storage.plugins_titles_to_names[dpg.get_value("list_of_plugins")]
    storage.set_prior_plugin_settings([current_plugin, storage.crosshair[2]], 
    [mouse_pos[0] - window_pos[0] + x_scroll, mouse_pos[1] - window_pos[1] + y_scroll])
    dpg.delete_item("image_mouse_tooltip")
    # назначить соответствующие значения инпутам
    parent = dpg.get_item_parent(storage.crosshair[1])
    children = dpg.get_item_children(parent, slot=1)
    dpg.set_value(children[0], mouse_pos[0] - window_pos[0] + x_scroll)
    dpg.set_value(children[1], mouse_pos[1] - window_pos[1] + y_scroll)
    storage.set_value(keys.CROSSHAIR, [False, None, None])

# при нажатии кнопки перекрестия кнопка дезактвируется, а актвируется режим "перекрестия"
def set_crosshair_mode(sender, app_data, user_data):
    if len(storage.opened_objects) == 0:
        return
    if storage.crosshair[0] == False:
        pv.zoom("100")
        dpg.bind_item_theme(sender, themes.get_green_crosshair_button_theme())
        dpg.add_tooltip("main_image_desk", tag="image_mouse_tooltip")
        dpg.add_text("(0, 0)", parent="image_mouse_tooltip", tag="image_mouse_tooltip_text")
        #dpg.bind_item_handler_registry("main_image_desk", "image_handler_registry")
        dpg.show_item("image_handler_registry")
        storage.set_value(keys.CROSSHAIR, [True, sender, user_data])
    else:
        dpg.bind_item_theme(sender, themes.get_crosshair_button_theme())
        dpg.delete_item("image_mouse_tooltip")
        #dpg.bind_item_handler_registry("main_image_desk", "none_handler")
        dpg.hide_item("image_handler_registry")
        storage.set_value(keys.CROSSHAIR, [False, None, None])