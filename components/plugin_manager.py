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
import components.custom_components as cc

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

def set_plugin_settings(sender):
    current_plugin_label = dpg.get_item_label(dpg.get_item_parent(dpg.get_item_parent(sender)))
    current_plugin = storage.plugins_titles_to_names[current_plugin_label]
    storage.set_plugin_settings(current_plugin, storage.plugins_settings[current_plugin])
    #with open('C:\ProgramData\cv_experiments\settings.json', 'w') as write_file:
    #    json.dump(storage.plugins_settings, write_file, indent=4, ensure_ascii=True)
    # обновление настроек
    if not storage.current_object is None:
        if storage.current_object['type'] == OBJECT_TYPES.image:
            pv.open_cv(storage.current_object)
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
    set_plugin_settings(None, selection[0], storage.current_file_field_tag['var'])

def open_plugins_window():
    dpg.show_item("plugins_window")

def apply_chain():
    if storage.current_object['type'] in (OBJECT_TYPES.image, OBJECT_TYPES.url):
        pv.open_cv(storage.current_object)
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

def add_plugin(label):
    x_scroll = dpg.get_x_scroll("plugin_node_editor_window")
    content_region_avail = dpg.get_item_state("plugin_node_editor_window")['content_region_avail']
    pos_x = content_region_avail[0] / 2 + x_scroll
    current_plugin = storage.plugins_titles_to_names[label]
    interface = storage.plugins[current_plugin].get('interface')
    plugin_settings = storage.plugins_settings[current_plugin]
    with dpg.node(label=label, pos=(pos_x, 0), parent="plugin_node_editor"):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
            dpg.add_text("Ввод")
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            if not interface is None:
                cc.add_plugin_settings(interface, current_plugin, plugin_settings)
            else:
                dpg.add_text("У этого плагина нет настроек")
                dpg.bind_item_font(dpg.last_item(), "mini_node_italic")
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_text("Результат обработки")
        dpg.enable_item("save_to_file_button")
        dpg.enable_item("open_warning_clear_desk_button")
   
#def delete_from_chain():
#    plugin_title = dpg.get_value("plugins_in_chain")
#    if plugin_title:
#        storage.set_value(keys.CHAIN_OF_PLUGINS, 
#        list(filter(lambda x: x != plugin_title, storage.chain_of_plugins)))
#        dpg.configure_item("plugins_in_chain", items=storage.chain_of_plugins)
#    if not storage.current_object is None:
#        pv.open_cv(**storage.current_object)
#    if len(storage.chain_of_plugins) != 0:
#        dpg.configure_item("plugins_in_chain", default_value=storage.chain_of_plugins[0])
#    check_plugin(None, dpg.get_value("list_of_plugins"), None)

# проверка плагина при нажатии на него в списке плагинов
#def check_plugin(sender, app_data, user_data):
#    show_previous(sender, app_data, user_data)
#    set_enable_delete_button(sender, app_data, user_data)
#    check_exist_in_chain(sender, app_data, user_data)
    ## Check have interface
#    plugin_name = storage.plugins_titles_to_names[app_data]
#    plugin = storage.plugins[plugin_name]
#    if plugin['interface'] is None:
#        dpg.disable_item("open_settings_button")
#    else:
#        dpg.enable_item("open_settings_button")

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
        add_plugin(title=plugin_title)
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
#def set_plugin_in_list(sender, app_data, user_data):
#    dpg.set_value("list_of_plugins", app_data)
#    check_plugin(sender, app_data, user_data)

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

def clear_desk():
    node_input_image_pos = dpg.get_item_pos("node_input_image")
    node_output_image_pos = dpg.get_item_pos("node_output_image")
    dpg.delete_item("plugin_node_editor", children_only=True)

    with dpg.node(label="Изображение", pos=node_input_image_pos, tag="node_input_image", 
    parent="plugin_node_editor"):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_text("Исходное изображение")
        dpg.bind_item_theme("node_input_image", themes.node_input())

    with dpg.node(label="Вывод", pos=node_output_image_pos, tag="node_output_image", 
    parent="plugin_node_editor"):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
            dpg.add_text("Обработанное изображение")
        dpg.bind_item_theme("node_output_image", themes.node_output())

    #storage.set_initial_nodes(node_input_image, node_output_image)
    dpg.disable_item("open_warning_clear_desk_button")
    dpg.disable_item("save_to_file_button")
    dpg.hide_item("warning_clear_desk")
    storage.clear_initial_inputs()

def link_nodes(sender, app_data):
    if not app_data[0] in storage.node_links and not app_data[1] in storage.node_links:
        node_link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        storage.add_to_node_links(app_data)
        dpg.set_item_user_data(node_link, app_data)

def delink_node(sender, app_data):
    node_data = dpg.get_item_user_data(app_data)
    dpg.delete_item(app_data)
    storage.remove_from_node_links(node_data)

def get_selected_nodes():
    selected_nodes = dpg.get_selected_nodes("plugin_node_editor")
    selected_links = dpg.get_selected_links("plugin_node_editor")
    node_input_id = None
    node_output_id = None

    for node in selected_nodes:
        if dpg.get_item_label(node) == "Изображение":
            storage.set_initial_input_id(node)
            node_input_id = node
            continue
        if dpg.get_item_label(node) == "Вывод":
            storage.set_initial_output_id(node)
            node_output_id = node
        if not node_input_id is None and not node_output_id is None:
            break

    if not node_input_id is None and node_input_id in selected_nodes:
        selected_nodes.remove(node_input_id)

    if not node_output_id is None and node_output_id in selected_nodes:
        selected_nodes.remove(node_output_id)

    if len(selected_links) > 0 or len(selected_nodes) > 0:
        dpg.enable_item("delete_nodes_button")

    if len(selected_links) == 0 and len(selected_nodes) == 0:
        dpg.disable_item("delete_nodes_button")

def delete_nodes_and_links():
    selected_nodes = dpg.get_selected_nodes("plugin_node_editor")
    selected_links = dpg.get_selected_links("plugin_node_editor")
    for link in selected_links:
        dpg.delete_item(link)

    for node in selected_nodes:
        if len(storage.initial_nodes_id) > 0 and storage.initial_nodes_id[0] == node:
            continue

        if len(storage.initial_nodes_id) > 1 and storage.initial_nodes_id[1] == node:
            continue

        dpg.delete_item(node)

    dpg.disable_item("delete_nodes_button")