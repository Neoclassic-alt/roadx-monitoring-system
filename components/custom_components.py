import dearpygui.dearpygui as dpg
import components.interface_functions as inf
import components.styling as themes
from components.storage import OBJECT_TYPES, OBJECT_STATUSES, storage, keys
import components.file_operations as fo
import components.plugin_manager as pm

def add_menu_item(label, callback=None, shortcut=None, tag=None, 
spacer_width=0, disabled=False, demo=False, width=255):
    with dpg.child_window(height=32, width=width, tag=tag, user_data={"disabled": disabled}):
        dpg.add_spacer(height=1)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=10)
            if disabled:
                dpg.add_text(label, color=(194, 194, 194))
            if not disabled:
                dpg.add_text(label)
            if demo:
                with dpg.group():
                    dpg.add_spacer()
                    dpg.add_image("demo_badge")
            dpg.add_spacer(width=spacer_width)
            if not shortcut is None:
                dpg.add_text(shortcut, color=(194, 194, 194))

    dpg.bind_item_theme(tag, "default_menu_item_theme")
    dpg.bind_item_handler_registry(tag, inf.buttonize_menu_item(tag, callback))

    if disabled:
        disable_menu_item(tag)

def enable_menu_item(tag, menu_item="default"):
    dpg.show_item(f"{tag}_move_handler")
    children = dpg.get_item_children(f"{tag}_handler", slot=1)
    dpg.show_item(children[0])
    dpg.show_item(children[1])
    dpg.show_item(children[2])
    if menu_item == "default":
        dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[1], color=(51, 51, 51))
    if menu_item == "plugin":
        dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[0], color=(51, 51, 51))
    dpg.set_item_user_data(tag, user_data={"disabled": False})

def disable_menu_item(tag, menu_item="default"):
    if menu_item == "default":
        dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[1], color=(194, 194, 194))
    if menu_item == "plugin":
        dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[0], color=(194, 194, 194))
    dpg.hide_item(f"{tag}_move_handler")
    children = dpg.get_item_children(f"{tag}_handler", slot=1)
    dpg.hide_item(children[0])
    dpg.hide_item(children[1])
    dpg.hide_item(children[2])
    dpg.set_item_user_data(tag, user_data={"disabled": True})

def add_file_item(filename, type_, status=OBJECT_STATUSES.new, short_url=None, current=False, 
extra_directory=False):
    height = 32
    if extra_directory:
       height = 52
    with dpg.group(horizontal=True, parent="file_filter_container", filter_key=filename):
        with dpg.child_window(width=-52, height=height, tag=f"file_{filename}"):
            dpg.add_spacer(height=1)
            with dpg.group(horizontal=True):
                if type_ == OBJECT_TYPES.stream:
                    type_ = "camera"
                if status == OBJECT_STATUSES.new:
                    dpg.add_image(type_)
                else:
                    dpg.add_image(f"{type_}_{status}")
                dpg.add_text(short_url or filename)
                if current:
                    dpg.add_image("current_file")
            if extra_directory:
                dpg.add_text(extra_directory, color=(194, 194, 194), tag=f"extra_{filename}")
                dpg.bind_item_font(dpg.last_item(), "micro_font")
        dpg.add_image_button("close_small", callback=lambda: fo.close_object(filename))
        dpg.bind_item_theme(dpg.last_item(), "close_button_theme")
        if not current:
            handler_registry = inf.buttonize(f"file_{filename}", lambda: fo.change_object(filename))
            dpg.bind_item_handler_registry(f"file_{filename}", handler_registry)

def set_file_current(filename):
    file_group = dpg.get_item_children(f"file_{filename}", slot=1)[1]
    dpg.add_image("current_file", parent=file_group)

def delete_file_current(filename):
    file_group = dpg.get_item_children(f"file_{filename}", slot=1)[1]
    dpg.delete_item(dpg.get_item_children(file_group, slot=1)[2])

def set_time_to_show_tooltip(sender, app_data):
    user_data = dpg.get_item_user_data(app_data)
    user_data["hover_time"] += dpg.get_delta_time()
    dpg.set_item_user_data(app_data, user_data)
    if user_data["hover_time"] >= 1:
        plugin_group = dpg.get_item_parent(app_data)
        dpg.show_item(dpg.get_item_children(plugin_group, slot=1)[1])

def add_plugin_item(label, info=None, favorite=False, in_favorites_list=False):
    parent = None
    tag = None
    if in_favorites_list:
        parent = "list_of_favorites"
        tag = f"{label}_plugin_in_favorites"
    else:
        parent = "plugin_list_filter"
        tag = f"{label}_plugin"
    with dpg.group(horizontal=True, parent=parent, filter_key=label, tag=tag, show=not in_favorites_list or favorite):
        button = dpg.add_button(label=label, width=-48, height=28, callback=lambda: pm.add_plugin(label), user_data={"hover_time": 0})
        dpg.bind_item_handler_registry(button, "plugin_button_registry")
        if not info is None:
            with dpg.tooltip(dpg.last_item(), show=False):
                dpg.add_spacer(height=2)
                dpg.add_text(info["title"] + "   ", wrap=400, indent=10)
                dpg.bind_item_font(dpg.last_item(), "tab_title")
                dpg.add_spacer()
                if not info.get("author") is None:
                    dpg.add_text("Автор: " + info["author"] + "   ", wrap=400, indent=10)
                if not info.get("version") is None:
                    dpg.add_text("Версия: " + info["version"] + "   ", wrap=400, indent=10)
                if not info.get("description") is None:
                    dpg.add_text(info["description"] + "   ", wrap=400, indent=10)
                dpg.add_spacer(height=2)
        if not favorite and not in_favorites_list:
            dpg.add_image_button("star_add", callback=lambda: add_to_favorites(label))
            dpg.bind_item_theme(dpg.last_item(), "favourite_add")
        if favorite and not in_favorites_list:
            dpg.add_image_button("star", enabled=False)
        if in_favorites_list:
            dpg.add_image_button("star_dismiss", callback=lambda: delete_from_favorites(label))
            dpg.bind_item_theme(dpg.last_item(), "favourite_dismiss")
    dpg.bind_item_theme(tag, "popup_style")

def add_to_favorites(label):
    if len(storage.favorite_plugins) == 5:
        dpg.show_item("no_more_5_plugins")
        return
    dpg.show_item(f"{label}_plugin_in_favorites")
    dpg.configure_item(dpg.get_item_children(f"{label}_plugin", slot=1)[1], texture_tag="star", enabled=False)
    storage.add_plugin_to_favorites(label)
    dpg.hide_item("no_plugins_in_favorites")
    if len(storage.favorite_plugins) > 1:
        dpg.set_item_height("add_plugins_window", dpg.get_item_height("add_plugins_window") + 28)

def delete_from_favorites(label):
    dpg.hide_item(f"{label}_plugin_in_favorites")
    star_button = dpg.get_item_children(f"{label}_plugin", slot=1)[1]
    dpg.configure_item(star_button, texture_tag="star_add", enabled=True, 
    callback=lambda: add_to_favorites(label))
    dpg.bind_item_theme(star_button, "favourite_add")
    storage.delete_plugin_from_favorites(label)
    if len(storage.favorite_plugins) == 0:
        dpg.show_item("no_plugins_in_favorites")
    dpg.hide_item("no_more_5_plugins")
    if len(storage.favorite_plugins) > 1:
        dpg.set_item_height("add_plugins_window", dpg.get_item_height("add_plugins_window") - 28)

def add_plugin_settings(interface, name, title):
    width = 200
    for field in interface:
        if field['type'] != 'checkbox':
            with dpg.group(horizontal=True, horizontal_spacing=3):
                dpg.add_text(field['title']) # заголовок
                if field['type'] != 'combo' and field.get('settings') \
                and field['settings'].get('required'):
                    dpg.add_text("*", color=(255, 0, 0, 255))
                if not field.get('description') is None:
                    dpg.add_image("help_mini")
                    dpg.add_tooltip(dpg.last_item())
                    dpg.add_text(field['description'], parent=dpg.last_item(), wrap=width)

        multiline = False
        settings = {'min_value': 1, 'max_value': 999, 'int': False}
        default_value = field.get('default_value')
        var = field['var']

        # если необходима перезагрузка тяжёлого объекта
        def set_settings_with_reload(sender, app_data, user_data):
            pm.set_plugin_settings(sender, app_data, user_data)
            need_loads_data = [x for x in storage.data_loads if x["name"] == name]
            if len(need_loads_data) != 0:
                storage.edit_need_load(name, True)

        callback = pm.set_plugin_settings
        if field.get('heavy_reload'): # перезагрузка тяжёлого объекта
            callback = set_settings_with_reload

        if field['type'] == "input":
            if not field.get('settings') is None:
                if not field['settings'].get('multiline') is None:
                    multiline = field['settings']['multiline']
            dpg.add_input_text(default_value=default_value or "", multiline=multiline, 
            callback=callback, user_data=field['var'], width=width)
            storage.set_plugin_settings(title, var, default_value or "")

        if field['type'] == "file":
            with dpg.add_group(horizontal=True):
                dpg.add_input_text(default_value="", readonly=True, width=width / 2)
                dpg.add_button(label="Добавить файл", callback=lambda: pm.set_file_field(dpg.last_item(), var))
                storage.set_plugin_settings(title, var, "")

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
                default_value=default_value or 0, callback=callback, user_data=field['var'], width=width)
            else:
                dpg.add_slider_float(min_value=settings['min_value'], max_value=settings['max_value'], format="%.3g",
                default_value=default_value or 0, callback=callback, user_data=field['var'], width=width)
            storage.set_plugin_settings(title, var, default_value or 0)

        if field['type'] == '2d-point':
            # задание двух слайдеров от x до y
            # TODO: переделать для назначения сразу в настройки
            def set_settings_to_point(sender, app_data, user_data):
                current_node = dpg.get_item_parent(dpg.get_item_parent(dpg.get_item_parent(sender)))
                current_plugin_label = dpg.get_item_label(current_node)
                current_plugin = f"{current_plugin_label}##{current_node}"
                current_plugin_settings = storage.plugins_settings[current_plugin]["settings"]
                if user_data[0] == 'x':
                    storage.set_plugin_settings(f"{current_plugin_label}##{current_node}", user_data[1], 
                    [app_data, current_plugin_settings[user_data[1]][1]])
                if user_data[0] == 'y':
                    storage.set_plugin_settings(f"{current_plugin_label}##{current_node}", user_data[1], 
                    [current_plugin_settings[user_data[1]][0], app_data])
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
                field_width = width / 2 - 5
                if field.get('settings') is None or field['settings'].get('crosshair') is None \
                or field['settings']['crosshair']:
                    crosshair = True
                    field_width = width / 2 - 24
                dpg.add_input_int(min_value=settings["x_min"], max_value=settings["x_max"], 
                default_value=default_value[0], callback=set_settings_to_point, user_data=['x', field['var']]
                , width=field_width, min_clamped=True, max_clamped=True, step=0)
                dpg.add_input_int(min_value=settings["y_min"], max_value=settings["y_max"], 
                default_value=default_value[1], callback=set_settings_to_point, user_data=['y', field['var']]
                , width=field_width, min_clamped=True, max_clamped=True, step=0)
                if crosshair:
                    button = dpg.add_image_button("crosshair_img", width=15, height=15, 
                    callback=pm.set_crosshair_mode, user_data={'var': field['var'], 'plugin_title': title})
                    dpg.bind_item_theme(dpg.last_item(), "get_crosshair_button_theme")
                    with dpg.tooltip(button):
                        dpg.add_text("Наведите на изображение и нажмите в нужном месте")
                storage.set_plugin_settings(title, var, default_value)

        if field['type'] == 'checkbox':
            if not field.get('description') is None:
                with dpg.group(horizontal=True, horizontal_spacing=5):
                    dpg.add_checkbox(label=field['title'], default_value=default_value or False, callback=callback, 
            user_data=field['var'])
                    dpg.add_image("help_mini")
                    dpg.add_tooltip(dpg.last_item())
                    dpg.add_text(field['description'], parent=dpg.last_item())
            else:
                dpg.add_checkbox(label=field['title'], default_value=default_value or False, callback=callback, 
            user_data=field['var'])
            storage.set_plugin_settings(title, var, default_value or False)

        if field['type'] == 'combo':
            dpg.add_combo(items=field['settings'], callback=callback, user_data=field['var'], 
            default_value=default_value or field['settings'][0], width=width)
            storage.set_plugin_settings(title, var, default_value or field['settings'][0])

        if field['type'] == 'number':
            if not field.get('settings') is None:
                if not field['settings'].get('min') is None:
                    settings['min_value'] = field['settings']['min']
                if not field['settings'].get('max') is None:
                    settings['max_value'] = field['settings']['max']
                if not field['settings'].get('int') is None:
                    settings['int'] = field['settings']['int']
            if settings['int']:
                dpg.add_input_int(default_value=default_value or min(0, settings['min_value']), callback=callback, 
                user_data=field['var'], min_value=settings['min_value'], max_value=settings['max_value'], width=width)
            else:
                dpg.add_input_float(default_value=default_value or min(0, settings['min_value']), callback=callback, 
                user_data=field['var'], min_value=settings['min_value'], max_value=settings['max_value'], width=width, format="%.3g")
            storage.set_plugin_settings(title, var, default_value or min(0, settings['min_value']))

def plugin_node_menu_item(text, tag, selected=False, disabled=False, mode=None, all_frames=None, group=None):
    with dpg.child_window(width=259, height=32, parent="modes_of_processing", tag=f"{tag}_plugin_menu_item",
    user_data={"disabled": disabled, "selected": selected, "group": group}):
        dpg.add_spacer(height=1)
        with dpg.group(horizontal=True, indent=10 - selected*5, horizontal_spacing=7):
            if selected:
                dpg.add_image("selected")
                dpg.add_text(text, color=(64, 149, 227))
            elif not selected and not disabled:
                dpg.add_text(text)
            else:
                dpg.add_text(text, color=(194, 194, 194))
            
    def callback_menu_item():
        select_plugin_item_and_deselect_other(tag, group)
        if not mode is None:
            storage.set_value(keys.PROCESS_MODE, mode)
        if not all_frames is None:
            storage.set_value(keys.ALL_FRAMES, all_frames)

    dpg.bind_item_theme(f"{tag}_plugin_menu_item", "default_menu_item_theme")
    dpg.bind_item_handler_registry(f"{tag}_plugin_menu_item", 
    inf.buttonize_menu_item(f"{tag}_plugin_menu_item", callback_menu_item))

    if disabled:
        disable_menu_item(f"{tag}_plugin_menu_item", menu_item="plugin")

def deselect_plugin_item(tag):
    item_user_data = dpg.get_item_user_data(f"{tag}_plugin_menu_item")
    item_user_data["selected"] = False
    dpg.set_item_user_data(f"{tag}_plugin_menu_item", item_user_data)
    
    text_group = dpg.get_item_children(f"{tag}_plugin_menu_item", slot=1)[1]
    dpg.set_item_indent(text_group, 10)
    text_group_elems = dpg.get_item_children(text_group, slot=1)
    dpg.configure_item(text_group_elems[1], color=(51, 51, 51))
    dpg.delete_item(text_group_elems[0])

def select_plugin_item_and_deselect_other(tag, group):
    plugin_items = dpg.get_item_children("modes_of_processing", slot=1)
    for item in plugin_items:
        if dpg.get_item_type(item) == "mvAppItemType::mvChildWindow":
            item_user_data = dpg.get_item_user_data(item)
            if item_user_data["selected"] and item_user_data["group"] == group:
                deselect_plugin_item(dpg.get_item_alias(item).rpartition("_plugin_menu_item")[0])
                break

    item_user_data = dpg.get_item_user_data(f"{tag}_plugin_menu_item")
    item_user_data["selected"] = True
    dpg.set_item_user_data(f"{tag}_plugin_menu_item", item_user_data)

    text_group = dpg.get_item_children(f"{tag}_plugin_menu_item", slot=1)[1]
    dpg.set_item_indent(text_group, 5)
    text_item = dpg.get_item_children(text_group, slot=1)[0]
    dpg.configure_item(text_item, color=(64, 149, 227))
    dpg.add_image("selected", parent=text_group, before=text_item)

def enable_button(tag, text_tag):
    children = dpg.get_item_children(f"{tag}_handler", slot=1)
    dpg.show_item(children[0])
    dpg.show_item(children[1])
    dpg.show_item(children[2])
    dpg.show_item(f"{tag}_move_handler")
    dpg.configure_item(text_tag, color=(51, 51, 51))

def disable_button(tag, text_tag):
    children = dpg.get_item_children(f"{tag}_handler", slot=1)
    dpg.hide_item(children[0])
    dpg.hide_item(children[1])
    dpg.hide_item(children[2])
    dpg.hide_item(f"{tag}_move_handler")
    dpg.configure_item(text_tag, color=(194, 194, 194))