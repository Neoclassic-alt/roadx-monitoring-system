import dearpygui.dearpygui as dpg
import components.interface_functions as inf
import components.styling as themes
from components.storage import OBJECT_STATUSES, storage
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

    dpg.bind_item_theme(tag, themes.default_menu_item_theme())
    dpg.bind_item_handler_registry(tag, inf.buttonize_menu_item(tag, callback))

    if disabled:
        disable_menu_item(tag)

def enable_menu_item(tag):
    #open_file_menu_item_registry = inf.buttonize_menu_item(tag, callback)
    #dpg.bind_item_handler_registry(tag, open_file_menu_item_registry)
    dpg.show_item(f"{tag}_move_handler")
    dpg.show_item(f"{tag}_handler")
    dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[1], color=(51, 51, 51))
    dpg.set_item_user_data(tag, user_data={"disabled": False})

def disable_menu_item(tag):
    dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[1], color=(194, 194, 194))
    #dpg.bind_item_handler_registry(tag, "none_handler")
    dpg.hide_item(f"{tag}_move_handler")
    dpg.hide_item(f"{tag}_handler")
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
        dpg.bind_item_theme(dpg.last_item(), themes.close_button_theme())
        if not current:
            handler_registry = inf.buttonize(f"file_{filename}", lambda: fo.change_object(filename))
            dpg.bind_item_handler_registry(f"file_{filename}", handler_registry)

def set_file_current(filename):
    file_group = dpg.get_item_children(f"file_{filename}", slot=1)[1]
    dpg.add_image("current_file", parent=file_group)

def delete_file_current(filename):
    file_group = dpg.get_item_children(f"file_{filename}", slot=1)[1]
    dpg.delete_item(dpg.get_item_children(file_group, slot=1)[2])

def add_plugin_item(label, favorite=False, in_favorites_list=False):
    parent = None
    tag = None
    if in_favorites_list:
        parent = "list_of_favorites"
        tag = f"{label}_plugin_in_favorites"
    else:
        parent = "plugin_list_filter"
        tag = f"{label}_plugin"
    with dpg.group(horizontal=True, parent=parent, filter_key=label, tag=tag, show=not in_favorites_list or favorite):
        dpg.add_button(label=label, width=-48, height=28, callback=lambda: pm.add_plugin(label))
        if not favorite and not in_favorites_list:
            dpg.add_image_button("star_add", callback=lambda: add_to_favorites(label))
            dpg.bind_item_theme(dpg.last_item(), themes.favourite_add())
        if favorite and not in_favorites_list:
            dpg.add_image_button("star", enabled=False)
        if in_favorites_list:
            dpg.add_image_button("star_dismiss", callback=lambda: delete_from_favorites(label))
            dpg.bind_item_theme(dpg.last_item(), themes.favourite_dismiss())

def add_to_favorites(label):
    if len(storage.favorite_plugins) == 5:
        dpg.show_item("no_more_5_plugins")
        return
    dpg.show_item(f"{label}_plugin_in_favorites")
    dpg.configure_item(dpg.get_item_children(f"{label}_plugin", slot=1)[1], texture_tag="star", enabled=False)
    storage.add_plugin_to_favorites(label)
    dpg.hide_item("no_plugins_in_favorites")

def delete_from_favorites(label):
    dpg.hide_item(f"{label}_plugin_in_favorites")
    star_button = dpg.get_item_children(f"{label}_plugin", slot=1)[1]
    dpg.configure_item(star_button, texture_tag="star_add", enabled=True, 
    callback=lambda: add_to_favorites(label))
    dpg.bind_item_theme(star_button, themes.favourite_add())
    storage.delete_plugin_from_favorites(label)
    if len(storage.favorite_plugins) == 0:
        dpg.show_item("no_plugins_in_favorites")
    dpg.hide_item("no_more_5_plugins")

def add_plugin_settings(interface, current_plugin, plugin_settings):
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

        default_value = plugin_settings.get(field['var'])
        multiline = False
        settings = {'min_value': 1, 'max_value': 999, 'int': False}

        # если необходима перезагрузка тяжёлого объекта
        def set_settings_with_reload(sender):
            pm.set_plugin_settings(sender)
            need_loads_data = [x for x in storage.data_loads if x["name"] == current_plugin]
            if len(need_loads_data) != 0:
                storage.edit_need_load(current_plugin, True)

        callback = pm.set_plugin_settings
        if field.get('heavy_reload'): # перезагрузка тяжёлого объекта
            callback = set_settings_with_reload

        if field['type'] == "input":
            if not field.get('settings') is None:
                if not field['settings'].get('multiline') is None:
                    multiline = field['settings']['multiline']
            dpg.add_input_text(default_value=default_value, multiline=multiline, 
            callback=callback, user_data=field['var'], width=width)

        if field['type'] == "file":
            with dpg.add_group(horizontal=True):
                dpg.add_input_text(default_value="", readonly=True, width=width / 2)
                dpg.add_button(label="Добавить файл", callback=lambda: pm.set_file_field(dpg.last_item(), field['var']))

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
                default_value=default_value, callback=callback, user_data=field['var'], width=width)
            else:
                dpg.add_slider_float(min_value=settings['min_value'], max_value=settings['max_value'], 
                default_value=default_value, callback=callback, user_data=field['var'], width=width)

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
                storage.set_2d_point_plugin_settings([current_plugin, user_data[1]], get_point)
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
                if field.get('settings') is None or field['settings'].get('crosshair') is None or field['settings']['crosshair']:
                    crosshair = True
                    field_width = width / 2 - 24
                dpg.add_input_int(min_value=settings["x_min"], max_value=settings["x_max"], 
                default_value=default_value[0], callback=set_prior_settings_to_point, user_data=['x', field['var']]
                , width=field_width, min_clamped=True, max_clamped=True, step=0)
                dpg.add_input_int(min_value=settings["y_min"], max_value=settings["y_max"], 
                default_value=default_value[1], callback=set_prior_settings_to_point, user_data=['y', field['var']]
                , width=field_width, min_clamped=True, max_clamped=True, step=0)
                if crosshair:
                    button = dpg.add_image_button("crosshair_img", width=16, height=16, callback=pm.set_crosshair_mode, user_data=field['var'])
                    dpg.bind_item_theme(dpg.last_item(), themes.get_crosshair_button_theme())
                    with dpg.tooltip(button):
                        dpg.add_text("Наведите на изображение и нажмите в нужном месте")

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

        if field['type'] == 'combo':
            dpg.add_combo(items=field['settings'], callback=callback, user_data=field['var'], 
            default_value=default_value or field['settings'][0], width=width)

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
                min_value=settings['min_value'], max_value=settings['max_value'], width=width)
            else:
                dpg.add_input_float(default_value=default_value or 0, callback=callback, user_data=field['var'],
                min_value=settings['min_value'], max_value=settings['max_value'], width=width)