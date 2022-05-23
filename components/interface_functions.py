import dearpygui.dearpygui as dpg
import components.photo_video as pv
from components.storage import storage, keys
import components.utils as utils
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

def show_tool_panel():
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

def create_plots():
    for plugin_title, video_data in storage.video_data.items():
        video_data = storage.video_data[plugin_title]
        plugin = storage.plugins_titles_to_names[plugin_title.rpartition('##')[0]]
        plugin_info = storage.plugins[plugin]['info']
        x_axis_label = plugin_info.get('x_axis_label')
        y_axis_label = plugin_info.get('y_axis_label')
        plot_types = plugin_info.get('plot_types')
        series_labels = plugin_info.get('series_labels')
        series_colors = plugin_info.get('series_colors')
        smoothing = plugin_info.get('smoothing')

        # создать пункты комбоменю
        items = dpg.get_item_configuration("plots_combo")["items"]
        items.append(plugin_title)
        dpg.configure_item("plots_combo", items=items)

        # создать график(и)
        plot = dpg.add_plot(label=plugin_title, height=250, width=375, parent="video_plots_group", no_mouse_pos=True)
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
    items = dpg.get_item_configuration("plots_combo")["items"]
    items.append("Скорость обработки плагинами")
    dpg.configure_item("plots_combo", items=items)
    plot = dpg.add_plot(label="Скорость обработки плагинами", height=250, width=375, parent="video_plots_group", no_mouse_pos=True)
    dpg.add_plot_axis(dpg.mvXAxis, label='Номер кадра', parent=plot)
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

    if len(storage.video_data) >= 3:
        dpg.set_item_height("information_window", height=453)

def open_plugin_window(sender):
    dpg.show_item("plugin_window")
    dpg.delete_item("plugin_window", children_only=True)
    viewport_height = dpg.get_viewport_client_height()
    viewport_width = dpg.get_viewport_client_width()
    dpg.set_item_pos("plugin_window", ((viewport_width - 760) / 2, (viewport_height - 550) / 2))
    children = dpg.get_item_children("video_plots_group", slot=1)
    plot_label = dpg.get_value(sender)
    if plot_label == "Не выбрано":
        return
    plot_item = None
    for child in children:
        if dpg.get_item_configuration(child)['label'] == plot_label:
            plot_item = child
    dpg.add_plot(label=plot_label, width=750, height=500, tag="plot_in_window", parent="plugin_window", no_mouse_pos=True)
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

def buttonize(name, callback, disabled=False):
    with dpg.item_handler_registry(tag=f"{name}_handler") as handler_registry:
        dpg.add_item_hover_handler(callback=lambda: dpg.bind_item_theme(name, "hover_button_theme"), 
        show=not disabled)
        dpg.add_item_active_handler(callback=lambda: dpg.bind_item_theme(name, "active_button_theme"),
        show=not disabled)
        dpg.add_item_active_handler(callback=callback, show=not disabled)

    with dpg.handler_registry(tag=f"{name}_move_handler", show=not disabled):
        dpg.add_mouse_move_handler(callback=lambda: dpg.bind_item_theme(name, "default_button_theme"))

    return handler_registry

def buttonize_menu_item(name, callback):
    with dpg.item_handler_registry(tag=f"{name}_handler") as handler_registry:
        dpg.add_item_hover_handler(callback=lambda: dpg.bind_item_theme(name, "hover_menu_item_theme"))
        dpg.add_item_active_handler(callback=lambda: dpg.bind_item_theme(name, "active_menu_item_theme"))
        dpg.add_item_active_handler(callback=callback)

    with dpg.handler_registry(tag=f"{name}_move_handler", show=False):
        dpg.add_mouse_move_handler(callback=lambda: dpg.bind_item_theme(name, "default_menu_item_theme"))

    return handler_registry

def open_file_menu():
    dpg.show_item("file_menu_window")
    for file_menu_item in dpg.get_item_children("file_menu", slot=1):
        if dpg.get_item_type(file_menu_item) == "mvAppItemType::mvChildWindow":
            if dpg.get_item_user_data(file_menu_item)["disabled"] == False:
                item_alias = dpg.get_item_alias(file_menu_item)
                dpg.show_item(f"{item_alias}_move_handler")

def open_app_menu():
    dpg.show_item("app_menu_window")
    for app_menu_item in dpg.get_item_children("app_menu", slot=1):
        if dpg.get_item_type(app_menu_item) == "mvAppItemType::mvChildWindow":
            item_alias = dpg.get_item_alias(app_menu_item)
            dpg.show_item(f"{item_alias}_move_handler")

def close_all_menus():
    if not dpg.get_item_state("file_button")["hovered"]:
        dpg.hide_item("file_menu_window")
        for file_menu_item in dpg.get_item_children("file_menu", slot=1):
            if dpg.get_item_type(file_menu_item) == "mvAppItemType::mvChildWindow":
                if dpg.get_item_user_data(file_menu_item)["disabled"] == False:
                    item_alias = dpg.get_item_alias(file_menu_item)
                    dpg.hide_item(f"{item_alias}_move_handler")
    if not dpg.get_item_state("app_button")["hovered"]:
        dpg.hide_item("app_menu_window")
        for app_menu_item in dpg.get_item_children("app_menu", slot=1):
            if dpg.get_item_type(app_menu_item) == "mvAppItemType::mvChildWindow":
                item_alias = dpg.get_item_alias(app_menu_item)
                dpg.hide_item(f"{item_alias}_move_handler")
    if not dpg.get_item_state("expand_modes_button")["hovered"]:
        dpg.hide_item("modes_of_processing_window")
        for app_menu_item in dpg.get_item_children("app_menu", slot=1):
            if dpg.get_item_type(app_menu_item) == "mvAppItemType::mvChildWindow":
                item_alias = dpg.get_item_alias(app_menu_item)
                dpg.hide_item(f"{item_alias}_move_handler")

def open_plugins_window():
    dpg.show_item("plugins_window")
    dpg.configure_item("plugins_window", width=dpg.get_viewport_client_width(), height=dpg.get_viewport_client_height() - 36)
    dpg.show_item("plugin_node_editor_registry")
    dpg.configure_item("expand_window", pos=(dpg.get_viewport_client_width() - 70, dpg.get_viewport_client_height() - 70))
    dpg.hide_item("video_player_window")

def open_window_at_center(tag, parent_tag="objects_window"):
    dpg.show_item(tag)
    pos = [(dpg.get_item_width(parent_tag) - dpg.get_item_width(tag)) / 2, 
    (dpg.get_item_height(parent_tag) - dpg.get_item_height(tag)) / 2]
    dpg.set_item_pos(tag, pos)

def open_warning_clear_desk():
    dpg.show_item("warning_clear_desk")
    pos = [(dpg.get_item_width("plugins_window") - 342) / 2, (dpg.get_item_height("plugins_window") - 142) / 2]
    dpg.set_item_pos("warning_clear_desk", pos)

def resize_node_plugins_window():
    dpg.configure_item("expand_window", pos=(dpg.get_item_width("plugins_window") - 50, 
    dpg.get_item_height("plugins_window") - 50))

def update_viewport_title():
    demo = ""
    filename = ""
    if storage.demo:
        demo = " (DEMO)"
    if not storage.current_object is None:
        filename = f": {storage.current_object['url']}"
    dpg.set_viewport_title("RoadX Monitoring System" + filename)

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
    client_height = dpg.get_viewport_client_height()
    client_width = dpg.get_viewport_client_width()
    dpg.configure_item("main_image_child_window", height=client_height - 80, width=client_width)
    minus_width = 0
    minus_height = 0
    if dpg.get_item_height("main_image_desk") > client_height:
        minus_width = 16
    if dpg.get_item_width("main_image_desk") > client_width:
        minus_height = 16
    dpg.set_item_pos("video_player_window", (0, client_height - 134 - minus_height))
    dpg.set_item_width("video_player_window", client_width - minus_width)
    dpg.set_item_width("player_pan", client_width - 188 - minus_width)
    dpg.set_item_indent("player_buttons", (client_width / 2 - minus_width) - 108)

    dpg.set_item_indent("indent_group", (client_width - 540) / 2)
    dpg.set_item_height("vertical_splash_spacer", (client_height - 300) / 2)

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
        dpg.bind_item_theme("close_all_files_button", "close_all_objects_button_default")

def resize_file_explorer_window():
    file_explorer_width = dpg.get_item_width("file_explorer_window")
    dpg.set_item_width("spacer_between_help_and_close_button", file_explorer_width/2 - 156)

def open_processing_modes_window():
    dpg.show_item("modes_of_processing_window")
    window_width = dpg.get_item_width("plugins_window")
    dpg.configure_item("modes_of_processing_window", pos=(window_width - 274, 120))
    for mode_menu_item in dpg.get_item_children("modes_of_processing", slot=1):
        if dpg.get_item_type(mode_menu_item) == "mvAppItemType::mvChildWindow":
            item_alias = dpg.get_item_alias(mode_menu_item)
            dpg.show_item(f"{item_alias}_move_handler")

def open_information_window():
    dpg.show_item("information_window")
    dpg.hide_item("red_point_image")
    dpg.set_item_width("information_button", 116)

def change_camera_fields(sender, app_data, user_data):
    errored = dpg.get_item_user_data("connect_to_camera_window")["error"]
    if app_data == "Веб-камера":
        dpg.show_item("web-camera_group")
        dpg.hide_item("IP-camera_group")
        if not errored:
            dpg.configure_item("connect_to_camera_window", height=204, min_size=(400, 204), max_size=(1000, 204))
        else:
            dpg.configure_item("connect_to_camera_window", height=240, min_size=(400, 240), max_size=(1000, 240))
        dpg.enable_item("add_camera_button")
    if app_data == "IP-камера":
        dpg.show_item("IP-camera_group")
        dpg.hide_item("web-camera_group")
        if not errored:
            dpg.configure_item("connect_to_camera_window", height=275, min_size=(400, 275), max_size=(1000, 275))
        else:
            dpg.configure_item("connect_to_camera_window", height=311, min_size=(400, 311), max_size=(1000, 311))
        if len(dpg.get_value("camera_url")) == 0:
            dpg.disable_item("add_camera_button")

def show_image_data_frame(sender, app_data):
    dpg.delete_item("info_from_image", children_only=True)
    info = storage.additional_data.get(app_data)
    if not info is None:
        for plugin in info:
            part = plugin["plugin"].rpartition('##')
            dpg.add_text(f"{part[0]} (ID {part[2]})", parent="info_from_image", wrap=-20)
            if len(plugin["text"]):
                dpg.add_text(plugin["text"], parent="info_from_image", wrap=-20)
                dpg.bind_item_font(dpg.last_item(), "mini_font")
            else:
                dpg.add_text("Информации нет", parent="info_from_image", wrap=-20)
                dpg.bind_item_font(dpg.last_item(), "mini_italic")
            dpg.add_spacer(height=5, parent="info_from_image")
    else:
            dpg.add_text("Для данного изображении нет информации", parent="info_from_image", wrap=-20)

def show_violations():
    dpg.delete_item("fixed_violations", children_only=True)
    if len(storage.violation_cases):
        THRESHOLD_TIME = 1 # коэффициент отсеивания в секундах
        FRAME_RATE = storage.frame_rate # кол-во кадров в секунду
        THRESHOLD = int(FRAME_RATE*THRESHOLD_TIME) # минимальная ширина диапазона
        plural_form = utils.plural(THRESHOLD, "кадр", "кадра", "кадров")
        dpg.hide_item("no_violations_text")
        dpg.show_item("minimal_range_size_text")
        dpg.set_value("minimal_range_size_text", f"Минимальная длина диазапона: {THRESHOLD} {plural_form}")
        dpg.show_item("place_open_in_range_group")
        for plugin, indexes in storage.violation_cases.items():
            name, _, id = plugin.rpartition('##')
            with dpg.group(horizontal=True, horizontal_spacing=5, parent="fixed_violations"):
                dpg.add_text(name)
                dpg.bind_item_font(dpg.last_item(), "tab_title")
                with dpg.group():
                    dpg.add_spacer()
                    dpg.add_text(f"(ID: {id})")
                dpg.bind_item_font(dpg.last_item(), "mini_font")
            with dpg.group(horizontal=True, parent="fixed_violations"):
                dpg.add_text("Выберите диапазон кадров: ")
                with dpg.group():
                    dpg.add_spacer()
                    dpg.add_combo(("Не выбрано", *utils.convert_to_ranges(indexes, THRESHOLD, FRAME_RATE)), 
                    width=300, default_value="Не выбрано", callback=open_violation_frames)
                    dpg.bind_item_theme(dpg.last_item(), "combo_style_2")
            dpg.add_spacer(height=3, parent="fixed_violations")
    else:
        dpg.show_item("no_violations_text")
        dpg.hide_item("minimal_range_size_text")
        dpg.hide_item("place_open_in_range_group")

def open_violation_frames(sender, app_data):
    if app_data == "Не выбрано":
        return
    position = dpg.get_value("place_open_in_range")
    if position == "начале":
        frame = int(app_data.split('–')[0])
    elif position == "середине":
        ttt = app_data.split(' ')[0].split('–')
        begin = int(ttt[0]) 
        end = int(ttt[1]) 
        frame = int((begin + end) / 2)
    elif position == "конце":
        ttt = app_data.split(' ')[0].split('–')
        frame = int(ttt[1])
    pv.open_frame(int(frame))
