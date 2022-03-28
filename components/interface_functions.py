import dearpygui.dearpygui as dpg
from components.storage import storage, keys
import pyperclip as clipboard
import components.styling as themes
import components.interface_functions as inf
import os

def change_video_texture(shape):
    dpg.delete_item("main_image_desk")
    with dpg.texture_registry():
        dpg.add_raw_texture(shape[1], shape[0], storage.current_data, format=dpg.mvFormat_Float_rgba, tag="main_image_desk")

def set_group_program_name_visible(sender, app_data):
    if app_data == "Программное имя":
        dpg.show_item("program_text_field")
    if app_data == "Исходные имена":
        dpg.hide_item("program_text_field")

def save_program_settings():
    qop = dpg.get_value("quality_of_pictures")
    auto_apply = dpg.get_value("auto_process_images")
    send_signal = dpg.get_value("send_beep")
    display_image_process = dpg.get_value("display_image_process")
    display_video_process = dpg.get_value("display_video_process")
    new_settings = {"quality_of_pictures": qop, "auto_apply": auto_apply, "send_signal": send_signal,
    "display_image_process": display_image_process, "display_video_process": display_video_process}
    storage.set_value(keys.PROGRAM_SETTINGS, new_settings)
    dpg.show_item("settings_of_program_have_saved")
    if auto_apply:
        dpg.hide_item("apply_chain_of_plugins_button")
    else:
        dpg.show_item("apply_chain_of_plugins_button")

def manage_all_headers(signal):
    items = dpg.get_item_children("additional_text_group")[1]
    if signal == "roll up":
        for item in items:
            dpg.configure_item(item, default_open=False)
    if signal == "expand":
        for item in items:
            dpg.configure_item(item, default_open=True)

def create_plots():
    for plugin_title, video_data in storage.video_data.items():
        video_data = storage.video_data[plugin_title]
        plugin = storage.plugins_titles_to_names[plugin_title]
        plugin_info = storage.plugins[plugin]['info']
        x_axis_label = plugin_info.get('x_axis_label')
        y_axis_label = plugin_info.get('y_axis_label')
        plot_types = plugin_info.get('plot_types')
        series_labels = plugin_info.get('series_labels')
        series_colors = plugin_info.get('series_colors')
        smoothing = plugin_info.get('smoothing')

        # создать кнопки
        dpg.add_button(label=plugin_title, parent="plot_buttons", user_data=plugin_title, callback=open_plugin_window)

        # создать график(и)
        plot = dpg.add_plot(label=plugin_title, height=250, width=375, parent="video_data_group", no_mouse_pos=True)
        dpg.add_plot_axis(dpg.mvXAxis, label=x_axis_label, parent=plot)
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label=y_axis_label, parent=plot)
        line_series_parameters = {}

        if len(video_data[0]) == 2:
            x_series = []
            y_series = []
            for x, y in video_data:
                x_series.append(x)
                y_series.append(y)
            if not smoothing is None:
                y_series = inf.smooth_series(y_series)
            line_series_parameters = {"x": x_series, "y": y_series, "parent": y_axis}
        if len(video_data[0]) == 3:
            # разделить по сериям
            divided_series = {1: [[], []], 2: [[], []], 3: [[], []]}
            for x, y, s in video_data:
                divided_series[s][0].append(x)
                divided_series[s][1].append(y)
            if not smoothing is None:
                for i in range(1, 3):
                    divided_series[i][1] = inf.smooth_series(divided_series[i][1])
        if not series_labels is None:
            dpg.add_plot_legend(parent=plot)
            line_series_parameters["label"] = series_labels[0]
        if len(video_data[0]) == 2:
            if plot_types[0] == "line":
                dpg.add_line_series(**line_series_parameters)
            if plot_types[0] == "stem":
                dpg.add_stem_series(**line_series_parameters)
            if plot_types[0] == "bar":
                dpg.add_bar_series(**line_series_parameters)
            if plot_types[0] == "pie":
                dpg.add_pie_series(**line_series_parameters)
            if plot_types[0] == "shade":
                dpg.add_shade_series(**line_series_parameters)
            if plot_types[0] == "area":
                dpg.add_area_series(**line_series_parameters)
        if len(video_data[0]) == 3:
            for i, plot_type in enumerate(plot_types):
                line_series_parameters = {"x": divided_series[i + 1][0], "y": divided_series[i + 1][1], "parent": y_axis}
                if not series_labels is None:
                    line_series_parameters["label"] = series_labels[i]
                if plot_type == "stem":
                    dpg.add_stem_series(**line_series_parameters)
                if plot_type == "line":
                    dpg.add_line_series(**line_series_parameters)
                if plot_type == "bar":
                    dpg.add_bar_series(**line_series_parameters)
                if not series_colors is None and len(series_colors) > i and not series_colors[i] is None:
                    dpg.bind_item_theme(dpg.last_item(), themes.get_line_fill_theme(series_colors[i]))

    # графики скорости обработки
    dpg.add_button(label="Скорость обработки плагинами", parent="plot_buttons", user_data="Скорость обработки плагинами", callback=open_plugin_window)
    plot = dpg.add_plot(label="Скорость обработки плагинами", height=250, width=375, parent="video_data_group", no_mouse_pos=True)
    x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='Номер кадра', parent=plot)
    #dpg.add_plot_legend(parent=plot)
    y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='Время обработки, с', parent=plot)
    x_series = list(range(storage.total_frames))
    y_all_series = []
    total_time = 0
    for y_series in storage.process_times:
        total_time += sum(y_series)
    for i in range(len(storage.chain_of_plugins)):
        y_all_series.append([])
    for i, plugin_title in enumerate(storage.chain_of_plugins):
        for j in range(storage.total_frames):
            y_all_series[i].append(storage.process_times[j][i])
    for i in range(1, len(y_all_series)):
        for j in range(len(y_all_series[0])):
            y_all_series[i][j] += y_all_series[i - 1][j]
    for i, plugin_title in enumerate(reversed(storage.chain_of_plugins)):
        dpg.add_bar_series(x_series, y_all_series[len(y_all_series) - i - 1], label=plugin_title, parent=y_axis)

    sum_last_plugin = sum(storage.process_times[-1])
    total_time_text = None
    if total_time > 60:
        total_time_text = f"Итоговое время: {round(total_time // 60)} мин {round(total_time % 60, 2)} с".replace('.', ',')
    else:
        total_time_text = f"Итоговое время: {round(total_time, 2)} с".replace('.', ',')

    dpg.add_plot_annotation(label=total_time_text, default_value=(storage.total_frames - 1, sum_last_plugin), 
    offset=(-15, -15), color=(113, 226, 0, 150), parent=plot, clamped=False)

def open_plugin_window(sender, app_data, user_data):
    dpg.show_item("plugin_window")
    dpg.delete_item("plugin_window", children_only=True)
    children = dpg.get_item_children("video_data_group", slot=1)
    plot_item = None
    for child in children:
        if dpg.get_item_configuration(child)['label'] == user_data:
            plot_item = child
    dpg.add_plot(label=user_data, width=750, height=500, tag="plot_in_window", parent="plugin_window", no_mouse_pos=True)
    children = dpg.get_item_children(plot_item)
    plotx_configuration = dpg.get_item_configuration(children[1][0])
    ploty_configuration = dpg.get_item_configuration(children[1][1])
    dpg.add_plot_legend(parent="plot_in_window")
    dpg.add_plot_axis(dpg.mvXAxis, label=plotx_configuration['label'], parent="plot_in_window")
    y_axis = dpg.add_plot_axis(dpg.mvYAxis, label=ploty_configuration['label'], parent="plot_in_window")
    for child in dpg.get_item_children(children[1][1], slot=1):
        series = dpg.get_item_configuration(child)
        value = dpg.get_value(child)
        theme = dpg.get_item_theme(child)
        if dpg.get_item_info(child)['type'] == 'mvAppItemType::mvBarSeries':
            dpg.add_bar_series(x=value[0], y=value[1], label=series['label'], parent=y_axis)
        if dpg.get_item_info(child)['type'] == 'mvAppItemType::mvStemSeries':
            dpg.add_stem_series(x=value[0], y=value[1], label=series['label'], parent=y_axis)
        if dpg.get_item_info(child)['type'] == 'mvAppItemType::mvLineSeries':
            dpg.add_stem_series(x=value[0], y=value[1], label=series['label'], parent=y_axis)
        dpg.bind_item_theme(dpg.last_item(), theme)

def set_hover_state(name):
    dpg.bind_item_theme(name, themes.hover_button_theme())

def set_active_state(name):
    dpg.bind_item_theme(name, themes.active_button_theme())

def set_default_state(name):
    dpg.bind_item_theme(name, themes.default_button_theme())

def buttonize(name, callback):
    with dpg.item_handler_registry(tag=f"{name}_handler") as handler_registry:
        dpg.add_item_hover_handler(callback=lambda: set_hover_state(name))
        dpg.add_item_active_handler(callback=lambda: set_active_state(name))
        dpg.add_item_active_handler(callback=callback)

    callback = lambda: set_default_state(name)
    with dpg.handler_registry(tag=f"{name}_move_handler"):
        dpg.add_mouse_move_handler(callback=callback)

    return handler_registry

def set_hover_menu_item_state(name):
    dpg.bind_item_theme(name, themes.hover_menu_item_theme())

def set_active_menu_item_state(name):
    dpg.bind_item_theme(name, themes.active_menu_item_theme())

def set_default_menu_item_state(name):
    dpg.bind_item_theme(name, themes.default_menu_item_theme())

def buttonize_menu_item(name, callback):
    with dpg.item_handler_registry(tag=f"{name}_handler", show=False) as handler_registry:
        dpg.add_item_hover_handler(callback=lambda: set_hover_menu_item_state(name))
        dpg.add_item_active_handler(callback=lambda: set_active_menu_item_state(name))
        dpg.add_item_active_handler(callback=callback)

    with dpg.handler_registry(tag=f"{name}_move_handler", show=False):
        dpg.add_mouse_move_handler(callback=lambda: set_default_menu_item_state(name))

    return handler_registry

def open_file_menu():
    dpg.show_item("file_menu_window")
    for file_menu_item in dpg.get_item_children("file_menu", slot=1):
        if dpg.get_item_type(file_menu_item) == "mvAppItemType::mvChildWindow":
            if dpg.get_item_user_data(file_menu_item)["disabled"] == False:
                item_alias = dpg.get_item_alias(file_menu_item)
                dpg.show_item(f"{item_alias}_move_handler")
                dpg.show_item(f"{item_alias}_handler")

def open_app_menu():
    dpg.show_item("app_menu_window")
    for app_menu_item in dpg.get_item_children("app_menu", slot=1):
        if dpg.get_item_type(app_menu_item) == "mvAppItemType::mvChildWindow":
            item_alias = dpg.get_item_alias(app_menu_item)
            dpg.show_item(f"{item_alias}_move_handler")
            dpg.show_item(f"{item_alias}_handler")

def close_all_menus():
    if not dpg.get_item_state("file_button")["hovered"]:
        dpg.hide_item("file_menu_window")
        for file_menu_item in dpg.get_item_children("file_menu", slot=1):
            if dpg.get_item_type(file_menu_item) == "mvAppItemType::mvChildWindow":
                if dpg.get_item_user_data(file_menu_item)["disabled"] == False:
                    item_alias = dpg.get_item_alias(file_menu_item)
                    dpg.hide_item(f"{item_alias}_move_handler")
                    dpg.hide_item(f"{item_alias}_handler")
    if not dpg.get_item_state("app_button")["hovered"]:
        dpg.hide_item("app_menu_window")
        for app_menu_item in dpg.get_item_children("app_menu", slot=1):
            if dpg.get_item_type(app_menu_item) == "mvAppItemType::mvChildWindow":
                item_alias = dpg.get_item_alias(app_menu_item)
                dpg.hide_item(f"{item_alias}_move_handler")
                dpg.hide_item(f"{item_alias}_handler")

def open_plugins_window():
    dpg.show_item("plugins_window")
    dpg.configure_item("plugins_window", width=dpg.get_viewport_client_width(), height=dpg.get_viewport_client_height())
    dpg.show_item("plugin_node_editor_registry")

def open_warning_clear_desk():
    dpg.show_item("warning_clear_desk")
    pos = [(dpg.get_viewport_client_width() - 342) / 2, (dpg.get_viewport_client_height() - 142) / 2]
    dpg.set_item_pos("warning_clear_desk", pos)

def update_viewport_title():
    demo = ""
    filename = ""
    if storage.demo:
        demo = " (DEMO)"
    if not storage.current_object is None:
        filename = f": {storage.current_object['url']}"
    dpg.set_viewport_title("RoadX Monitoring System" + demo + filename)

def update_status_bar_info():
    current_file = storage.current_object["url"]
    file_size = os.path.getsize(current_file) / 1024
    width = dpg.get_item_configuration("main_image")["width"]
    height = dpg.get_item_configuration("main_image")["height"]

    if file_size >= 1024:
        file_size = str(round(file_size / 1024, 2)) + " МБ"
    else:
        file_size = str(round(file_size, 2)) + " КБ"

    dpg.set_value("status_bar_info", f"Разрешение: {width}×{height}, размер: {file_size}")

def resize_viewport():
    dpg.configure_item("main_image_child_window", height=dpg.get_viewport_client_height() - 80, width=dpg.get_viewport_client_width())
    minus_width = 0
    minus_height = 0
    if dpg.get_item_height("main_image_desk") > dpg.get_viewport_client_height():
        minus_width = 16
    if dpg.get_item_width("main_image_desk") > dpg.get_viewport_client_width():
        minus_height = 16
    dpg.set_item_pos("video_player_window", (0, dpg.get_viewport_client_height() - 134 - minus_height))
    dpg.set_item_width("video_player_window", dpg.get_viewport_client_width() - minus_width)
    dpg.set_item_width("player_pan", dpg.get_viewport_client_width() - 188 - minus_width)
    dpg.set_item_indent("player_buttons", (dpg.get_viewport_client_width() / 2 - minus_width) - 108)

def open_file_explorer():
    dpg.show_item("file_explorer_window") 
    dpg.focus_item("search_field_input")

def apply_opacity_to_video_player(opacity):
    dpg.set_value("player_pan_theme", (255, 255, 255, opacity // 2))
    dpg.set_value("player_progress_theme", (64, 149, 227, opacity))
    dpg.set_value("player_window_theme", (0, 0, 0, opacity // 6.3))
    dpg.configure_item("skip_backward_button", tint_color=(255, 255, 255, opacity))
    dpg.configure_item("prev_frame_button", tint_color=(255, 255, 255, opacity))
    dpg.configure_item("play_button", tint_color=(255, 255, 255, opacity))
    dpg.configure_item("next_frame_button", tint_color=(255, 255, 255, opacity))
    dpg.configure_item("skip_forward_button", tint_color=(255, 255, 255, opacity))
    dpg.configure_item("lock_button", tint_color=(255, 255, 255, opacity))
    dpg.configure_item("time_video_from_begin", color=(255, 255, 255, opacity))
    dpg.configure_item("video_duration", color=(255, 255, 255, opacity))

def set_close_all_button_default():
    if not dpg.get_item_state("close_all_files_button")["hovered"]:
        dpg.bind_item_theme("close_all_files_button", themes.close_all_objects_button_default())

def resize_file_explorer_window():
    file_explorer_width = dpg.get_item_width("file_explorer_window")
    dpg.set_item_width("spacer_between_help_and_close_button", file_explorer_width/2 - 156)