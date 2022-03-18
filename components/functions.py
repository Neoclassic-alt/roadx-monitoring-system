import dearpygui.dearpygui as dpg
from components.storage import storage, keys
import pyperclip as clipboard
import components.styling as themes
import os

class AppInfo:
    def change_video_texture(shape):
        dpg.delete_item("main_image_desk")
        with dpg.texture_registry():
            dpg.add_raw_texture(shape[1], shape[0], storage.current_data, format=dpg.mvFormat_Float_rgba, tag="main_image_desk")

    def set_group_program_name_visible(sender, app_data):
        if app_data == "Программное имя":
            dpg.show_item("program_text_field")
        if app_data == "Исходные имена":
            dpg.hide_item("program_text_field")

    def load_font(url, size, tag = None):
        if not tag is None:
            with dpg.font(url, size, tag=tag):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                dpg.add_font_range(0x2190, 0x219e)
                dpg.add_font_range(0x2100, 0x214f)
                dpg.add_font_range(0x2010, 0x2015)
                dpg.add_font_chars([0x00D7])
        else:
            with dpg.font(url, size):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

    def copy_all_additional_data():
        all_additional_data = ''
        for additional_data in storage.additional_data:
            all_additional_data += f"Информация от плагина {additional_data['plugin']}\n"
            all_additional_data += f"{additional_data['text']}\n"
        clipboard.copy(all_additional_data)

    def plural(count, one_form, two_form, three_form):
        if (count % 10) == 1 and (count > 20 or count == 1):
            return one_form
        if (count % 10) >= 2 and (count % 10) <= 4 and (count > 20 or count < 10):
            return two_form
        if (count % 10) >= 5 or (count % 10) == 0 or (count >= 10 and count <= 20):
            return three_form

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

    def add_static_texture(url, tag):
        width, height, channels, data = dpg.load_image(url)
        dpg.add_static_texture(width, height, data, tag=tag)

    def smooth_series(y_series):
        # сглаживание
        AVG = 5
        for i in range(len(y_series) // AVG):
            #average = (y_series[i*AVG] + y_series[i*AVG+1] + y_series[i*AVG+2] + y_series[i*AVG+3] + y_series[i*AVG+4])/AVG
            median = [y_series[i*AVG], y_series[i*AVG+1], y_series[i*AVG+2], y_series[i*AVG+3], y_series[i*AVG+4]]
            median.sort()
            median = median[2]
            y_series[i*AVG] = median
            y_series[i*AVG+1] = median
            y_series[i*AVG+2] = median
            y_series[i*AVG+3] = median
            y_series[i*AVG+4] = median

        return y_series

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
            dpg.add_button(label=plugin_title, parent="plot_buttons", user_data=plugin_title, callback=AppInfo.open_plugin_window)

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
                    y_series = AppInfo.smooth_series(y_series)
                line_series_parameters = {"x": x_series, "y": y_series, "parent": y_axis}
            if len(video_data[0]) == 3:
                # разделить по сериям
                divided_series = {1: [[], []], 2: [[], []], 3: [[], []]}
                for x, y, s in video_data:
                    divided_series[s][0].append(x)
                    divided_series[s][1].append(y)
                if not smoothing is None:
                    for i in range(1, 3):
                        divided_series[i][1] = AppInfo.smooth_series(divided_series[i][1])
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
        dpg.add_button(label="Скорость обработки плагинами", parent="plot_buttons", user_data="Скорость обработки плагинами", callback=AppInfo.open_plugin_window)
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
            dpg.add_item_hover_handler(callback=lambda: AppInfo.set_hover_state(name))
            dpg.add_item_active_handler(callback=lambda: AppInfo.set_active_state(name))
            dpg.add_item_active_handler(callback=callback)

        dpg.add_mouse_move_handler(callback=lambda: AppInfo.set_default_state(name), parent="global_handlers")

        return handler_registry

    def set_hover_menu_item_state(name):
        dpg.bind_item_theme(name, themes.hover_menu_item_theme())

    def set_active_menu_item_state(name):
        dpg.bind_item_theme(name, themes.active_menu_item_theme())
    
    def set_default_menu_item_state(name):
        dpg.bind_item_theme(name, themes.default_menu_item_theme())

    def buttonize_menu_item(name, callback):
        with dpg.item_handler_registry(tag=f"{name}_handler") as handler_registry:
            dpg.add_item_hover_handler(callback=lambda: AppInfo.set_hover_menu_item_state(name))
            dpg.add_item_active_handler(callback=lambda: AppInfo.set_active_menu_item_state(name))
            dpg.add_item_active_handler(callback=callback)

        dpg.add_mouse_move_handler(callback=lambda: AppInfo.set_default_menu_item_state(name), parent="global_handlers")

        return handler_registry

    def close_all_menus():
        if not dpg.get_item_state("file_button")["hovered"]:
            dpg.hide_item("file_menu_window")
        if not dpg.get_item_state("app_button")["hovered"]:
            dpg.hide_item("app_menu_window")

    def update_viewport_title():
        demo = ""
        filename = ""
        if storage.demo:
            demo = " (DEMO)"
        if not storage.current_object is None:
            filename = f": {storage.current_object['url']}"
        dpg.set_viewport_title("RoadX Monitoring System" + demo + filename)

    def resize_image_window():
        dpg.configure_item("main_image_child_window", height=dpg.get_viewport_client_height() - 80, width=dpg.get_viewport_client_width())

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