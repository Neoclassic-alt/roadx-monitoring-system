import dearpygui.dearpygui as dpg
import components.utils as utils
import components.photo_video as pv
from components.storage import OBJECT_STATUSES, storage
from components.storage import keys
from components.storage import OBJECT_TYPES
import os
import json
import importlib
import components.styling as themes
import components.custom_components as cc

def load_plugins():
    PATH_TO_PLUGINS = "plugin_system/plugins"
    all_folders = os.listdir('.\plugin_system\plugins')
    plugins = {}
    for f8ile in all_folders:
        module_files = os.listdir(f'{PATH_TO_PLUGINS}/{f8ile}')
        is_plugin = True
        try:
            if not ('info.json' in module_files) or not f'main.py' in module_files:
                raise FileNotFoundError("В модуле нет файлов main.py и/или info.json")
        except Exception as e:
            print(e)
            is_plugin = False
        if is_plugin:
            plugins[f8ile] = {'info': '', 'interface': '', 'payload': None, 'transform': '', 'group': None}
            with open(f"{PATH_TO_PLUGINS}/{f8ile}/info.json", "r", encoding='utf-8') as json_file:
                plugins[f8ile]['info'] = json.load(json_file)
            # импорт плагина
            module = importlib.import_module(f'plugin_system.plugins.{f8ile}.main')
            if os.path.isfile(f"{PATH_TO_PLUGINS}/{f8ile}/interface.json"):
                with open(f"{PATH_TO_PLUGINS}/{f8ile}/interface.json", "r", encoding='utf-8') as interface_file:
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

def set_plugin_settings(sender, value, current_var):
    current_node = dpg.get_item_parent(dpg.get_item_parent(sender))
    current_plugin_label = dpg.get_item_label(current_node)
    storage.set_plugin_settings(f"{current_plugin_label}##{current_node}", current_var, value)

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
    create_chain()
    # начинаем вносить плагины в список
    if storage.current_object['type'] in (OBJECT_TYPES.image, OBJECT_TYPES.url):
        pv.open_cv(storage.current_object)
    if storage.current_object['type'] == OBJECT_TYPES.video:
        if storage.all_frames:
            pv.process_all_frames()
        pv.open_frame(storage.current_frame)
    storage.set_status(OBJECT_STATUSES.actual)

# загрузка "тяжёлых" данных
def load_heavy(plugin, parameters, single_image=True):
    dpg.show_item("state_of_loading")
    dpg.show_item("loading_indicator")
    dpg.hide_item("progress_bar")
    dpg.hide_item("status_bar_info")
    dpg.hide_item("time_evaluation")
    dpg.set_value("text_of_loading", "Загрузка плагина...")
    heavy = storage.plugins[plugin]['payload'](parameters)
    #dpg.hide_item("state_of_loading")
    if not single_image or storage.current_frame == 0:
        if len(storage.chain_of_plugins) == 1:
            dpg.set_value("text_of_loading", "Применение плагина к кадрам")
        if len(storage.chain_of_plugins) > 1:
            dpg.set_value("text_of_loading", "Применение плагинов к кадрам")
    return heavy

def create_chain():
    chain_of_plugins = []
    current_node = 'node_input_image'
    next_node = None
    node_plugins = storage.node_plugins
    while next_node != 'node_output_image':
        current_node, next_node = [link for link in node_plugins if link[0] == current_node][0]
        if next_node != 'node_output_image':
            chain_of_plugins.append(next_node)
            current_node = next_node
    chain_of_plugins = list(map(lambda plugin: f"{dpg.get_item_label(plugin)}##{plugin}", chain_of_plugins))
    storage.set_value(keys.CHAIN_OF_PLUGINS, chain_of_plugins)
    return chain_of_plugins

def toggle_node_settings(sender, app_data, user_data):
    if user_data["closed"]:
        dpg.show_item(user_data["plugin_settings_id"])
        user_data["closed"] = False
        dpg.set_item_label(sender, "Скрыть")
    else:
        dpg.hide_item(user_data["plugin_settings_id"])
        user_data["closed"] = True
        dpg.set_item_label(sender, "Раскрыть")
    dpg.set_item_user_data(sender, user_data)

def add_plugin(label):
    x_scroll = dpg.get_x_scroll("plugin_node_editor_window")
    content_region_avail = dpg.get_item_state("plugin_node_editor_window")['content_region_avail']
    pos_x = content_region_avail[0] / 2 + x_scroll
    current_plugin = storage.plugins_titles_to_names[label]
    interface = storage.plugins[current_plugin].get('interface')
    payload = storage.plugins[current_plugin].get('payload')
    with dpg.node(label=label, pos=(pos_x, 50), parent="plugin_node_editor") as plugin_id:
        storage.add_plugin(f"{label}##{plugin_id}", not payload is None) # добавляем словарь по имени
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            with dpg.group(horizontal=True) as id_group:
                dpg.add_text(f"ID: {plugin_id}")
                dpg.bind_item_font(dpg.last_item(), "node_items_font")
                warning_image = dpg.add_image("node_warning", show=False)
                dpg.add_tooltip(warning_image)
                dpg.bind_item_font(id_group, "tooltip_font")
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static) as plugin_settings:
            if not interface is None:
                cc.add_plugin_settings(interface, name=current_plugin, title=f"{label}##{plugin_id}")
            else:
                dpg.add_text("Нет настроек")
                dpg.bind_item_font(dpg.last_item(), "mini_node_italic")
        dpg.add_button(label="Скрыть", user_data={"closed": False, "plugin_settings_id": plugin_settings}, 
            callback=toggle_node_settings, parent=id_group, before=warning_image, show=not interface is None)
        dpg.bind_item_font(dpg.last_item(), "node_items_font")
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
            dpg.add_text("Ввод")
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
            with dpg.group(horizontal=True):
                plugin_info = storage.plugins[current_plugin]["info"]
                if not plugin_info.get("display") is None and "video_data" in plugin_info["display"]:
                    dpg.add_image("graph")
                dpg.add_text("Результат обработки")
        #dpg.enable_item("save_to_file_button")
        dpg.enable_item("open_warning_clear_desk_button")
    show_previous()
   
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

def get_mouse_pos():
    mouse_pos = dpg.get_mouse_pos(local=False)
    window_pos = dpg.get_item_pos("main_image_child_window")
    y_scroll = dpg.get_y_scroll("main_image_child_window")
    x_scroll = dpg.get_x_scroll("main_image_child_window")
    dpg.set_value("image_mouse_tooltip_text", f"({int(mouse_pos[0] - window_pos[0] + x_scroll)}, \
{int(mouse_pos[1] - window_pos[1] + y_scroll)})")

# функция при нажатии на картинку в crosshair_mode 
def set_2d_point_values():
    mouse_pos = dpg.get_mouse_pos(local=False)
    window_pos = dpg.get_item_pos("main_image_child_window")
    y_scroll = dpg.get_y_scroll("main_image_child_window")
    x_scroll = dpg.get_x_scroll("main_image_child_window")
    #dpg.hide_item("image_handler_registry")
    item_handlers = dpg.get_item_children("image_handler_registry", slot=1)
    dpg.hide_item(item_handlers[0])
    dpg.hide_item(item_handlers[1])
    dpg.show_item("plugins_window")
    dpg.bind_item_theme(storage.crosshair[1], "get_crosshair_button_theme")
    storage.set_plugin_settings(storage.crosshair[2]["plugin_title"], storage.crosshair[2]["var"], 
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
        dpg.hide_item("plugins_window")
        pv.zoom("100")
        dpg.bind_item_theme(sender, "get_green_crosshair_button_theme")
        dpg.add_tooltip("main_image_desk", tag="image_mouse_tooltip")
        dpg.add_text("(0, 0)", parent="image_mouse_tooltip", tag="image_mouse_tooltip_text")
        item_handlers = dpg.get_item_children("image_handler_registry", slot=1)
        dpg.show_item(item_handlers[0])
        dpg.show_item(item_handlers[1])
        storage.set_value(keys.CROSSHAIR, [True, sender, user_data])
    else:
        dpg.bind_item_theme(sender, "get_crosshair_button_theme")
        dpg.delete_item("image_mouse_tooltip")
        item_handlers = dpg.get_item_children("image_handler_registry", slot=1)
        dpg.hide_item(item_handlers[0])
        dpg.hide_item(item_handlers[1])
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
    dpg.disable_item("begin_processing_button")
    dpg.hide_item("warning_clear_desk")
    storage.clear_initial_inputs()

def link_nodes(sender, app_data):
    if not app_data[0] in storage.node_links and not app_data[1] in storage.node_links:
        node_link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        storage.add_to_node_links(app_data)
        storage.add_to_node_plugins(dpg.get_item_parent(app_data[0]), dpg.get_item_parent(app_data[1]))
        dpg.set_item_user_data(node_link, app_data)
    count_of_links = len(dpg.get_item_children("plugin_node_editor", slot=0))
    count_of_nodes = len(dpg.get_item_children("plugin_node_editor", slot=1))
    if count_of_links == count_of_nodes - 1 and not storage.current_object is None:
        dpg.enable_item("begin_processing_button")

def delink_node(sender, app_data):
    node_data = dpg.get_item_user_data(app_data)
    dpg.delete_item(app_data)
    storage.remove_from_node_links(node_data)
    storage.remove_from_node_plugins(dpg.get_item_parent(node_data[0]), dpg.get_item_parent(node_data[1]))
    dpg.disable_item("begin_processing_button")

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
        node_data = dpg.get_item_user_data(link)
        dpg.delete_item(link)
        storage.remove_from_node_links(node_data)
        storage.remove_from_node_plugins(dpg.get_item_parent(node_data[0]), dpg.get_item_parent(node_data[1]))

    for node in selected_nodes:
        if len(storage.initial_nodes_id) > 0 and storage.initial_nodes_id[0] == node:
            continue

        if len(storage.initial_nodes_id) > 1 and storage.initial_nodes_id[1] == node:
            continue

        dpg.delete_item(node)

    dpg.disable_item("delete_nodes_button")
    dpg.disable_item("begin_processing_button")
    show_previous()

### Проверка всех плагинов на наличие предыдущих
def show_previous():
    chain_of_plugins = []
    children_of_desk = dpg.get_item_children("plugin_node_editor", slot=1)
    for node in children_of_desk:
        if not dpg.get_item_alias(node) in ("node_input_image", "node_output_image"):
            chain_of_plugins.append(dpg.get_item_label(node) + "##" + str(node))
    previous = {} # с каждого плагина соберём информацию о предыдущих
    previous_titles = {} # имена предыдущих плагинов
    previous_exist = {} # имеются ли предыдущие плагины или нет
    for plugin in chain_of_plugins:
        plugin_title = plugin.rpartition('##')[0]
        plugin_name = storage.plugins_titles_to_names[plugin_title]
        plugin_previous = storage.plugins[plugin_name]["info"].get("previous")
        previous[plugin] = plugin_previous
    for plugin, previous_plugins in previous.items():
        if previous_plugins is None:
            continue
        exist = []
        plugins_titles = []
        for plugin_name in previous_plugins:
            plugin_title = storage.plugins[plugin_name]["info"]["title"]
            plugins_titles.append(plugin_title)
            need_plugins = [x for x in chain_of_plugins if x.startswith(plugin_title)]
            exist.append(bool(len(need_plugins)))
        previous_exist[plugin] = exist
        previous_titles[plugin] = plugins_titles
    for plugin_title, results in previous_exist.items():
        node_id = int(plugin_title.rpartition('##')[2])
        node_attribute = dpg.get_item_children(node_id, slot=1)[0]
        node_group = dpg.get_item_children(node_attribute, slot=1)[0]
        node_items = dpg.get_item_children(node_group, slot=1)
        dpg.delete_item(node_items[3], children_only=True)

        dpg.show_item(node_items[2])
        dpg.add_spacer(parent=node_items[3])
        if results.count(True) == len(results):
            dpg.configure_item(node_items[2], texture_tag="node_check")
            dpg.add_text("Все предыдущие плагины на месте", parent=node_items[3], indent=5)
        else:
            dpg.configure_item(node_items[2], texture_tag="node_warning")
            dpg.add_text("Не хватает предыдущих плагинов: ", parent=node_items[3], indent=5)

        exist_flag = False # хоть один предыдущий плагин присутствует

        for i, result in enumerate(results):
            if not result:
                dpg.add_text(previous_titles[plugin_title][i] + "  ", bullet=True, color=(250, 137, 137), 
                parent=node_items[3], indent=5)
            else:
                exist_flag = True
        
        if exist_flag:
            dpg.add_spacer(parent=node_items[3])
            dpg.add_text("Имеющиеся плагины: ", parent=node_items[3], indent=5)
            for i, result in enumerate(results):
                if result:
                    dpg.add_text(previous_titles[plugin_title][i] + "  ", bullet=True, parent=node_items[3], indent=5)

        dpg.add_spacer(parent=node_items[3])