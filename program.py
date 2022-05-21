import dearpygui.dearpygui as dpg
import components.utils as utils
from components.storage import OBJECT_TYPES, PROCESS_MODES
import components.key_module as key_module
import components.plugin_manager as pm
from components.storage import storage, keys
import components.styling as themes
import components.photo_video as pv
import components.file_operations as fo
import components.interface_functions as inf
import warnings
import pyperclip as clipboard
import time
import components.custom_components as cc
import components.assets as assets

# загрузка модулей
storage.set_value(keys.PLUGINS, pm.load_plugins())

# связываем заголовок плагина с его именем для нужд интерфейса
pm.set_titles_to_names()

# работа с usb
usbkey = key_module.USBKey()

# проверка, подключен ли ключ в систему
def check_connect():
    result = usbkey.check_connect()
    # ключ вытащен
    if not result and not storage.demo:
        usbkey.limit()

    # ключ вставлен
    if result and storage.demo:
        key_valid = usbkey.check_key()
        if key_valid:
            usbkey.unlock()

dpg.create_context()

with dpg.font_registry():
    with dpg.font(r"assets\fonts\NotoSans-Regular.ttf", 20) as main_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.add_font_range(0x2190, 0x219e)
        dpg.add_font_range(0x2100, 0x214f)
        dpg.add_font_range(0x2010, 0x2015)
    utils.load_font(r"assets\fonts\NotoSans-Bold.ttf", 24, tag="title")
    utils.load_font(r"assets\fonts\NotoSans-Regular.ttf", 24, tag="tab_title")
    utils.load_font(r"assets\fonts\NotoSans-Regular.ttf", 22, tag="warning_title")
    utils.load_font(r"assets\fonts\NotoSans-Regular.ttf", 18, tag="mini_font")
    utils.load_font(r"assets\fonts\NotoSans-Regular.ttf", 16, tag="micro_font")
    utils.load_font(r"assets\fonts\OpenSans-SemiBold.ttf", 20, tag="button_label")
    utils.load_font(r"assets\fonts\OpenSans-Medium.ttf", 16, tag="node_items_font")
    utils.load_font(r"assets\fonts\OpenSans-Italic.ttf", 18, tag="mini_italic")
    utils.load_font(r"assets\fonts\OpenSans-MediumItalic.ttf", 16, tag="mini_node_italic")
    utils.load_font(r"assets\fonts\OpenSans-SemiBold.ttf", 18, tag="tooltip_font")

assets.get_assets()

with dpg.handler_registry():
    dpg.add_mouse_release_handler(callback=pm.undragging)
    #dpg.add_key_press_handler(dpg.mvKey_Control, callback=lambda: dpg.show_item("settings_of_the_program"))
    #dpg.add_key_press_handler(dpg.mvKey_Control, callback=pm.apply_chain)
    #dpg.add_key_press_handler(dpg.mvKey_Control, callback=lambda: dpg.show_item("plugins_window"))
    dpg.add_mouse_release_handler(callback=inf.close_all_menus)
    dpg.add_mouse_move_handler(callback=lambda: storage.reset_video_timer())
    dpg.add_mouse_move_handler(callback=inf.set_close_all_button_default)

with dpg.item_handler_registry(tag="image_handler_registry"):
    dpg.add_item_hover_handler(callback=pm.get_mouse_pos, show=False)
    dpg.add_item_active_handler(callback=pm.set_2d_point_values, show=False)

file_button_registry = inf.buttonize("file_button", inf.open_file_menu)
app_button_registry = inf.buttonize("app_button", inf.open_app_menu)
information_button_registry = inf.buttonize("information_button", inf.open_information_window, 
disabled=True)

with dpg.item_handler_registry(tag="pan_handler_registry"):
    dpg.add_item_active_handler(callback=lambda: pv.open_frame(utils.convert_to_index()))

with dpg.item_handler_registry(tag="close_all_files_button_registry"):
    dpg.add_item_hover_handler(callback=lambda: 
    dpg.bind_item_theme("close_all_files_button", themes.close_all_objects_button_hover()))
    dpg.add_item_active_handler(callback=fo.close_all_objects)

with dpg.item_handler_registry(tag="resize_window_handler"):
    dpg.add_item_resize_handler(callback=inf.resize_file_explorer_window)

with dpg.handler_registry(tag="plugin_node_editor_registry", show=False):
    dpg.add_mouse_release_handler(callback=pm.get_selected_nodes)
    dpg.add_key_press_handler(dpg.mvKey_Delete, callback=pm.delete_nodes_and_links)

with dpg.item_handler_registry(tag="resize_node_plugins_window_handler"):
    dpg.add_item_resize_handler(callback=inf.resize_node_plugins_window)

with dpg.item_handler_registry(tag="plugin_button_registry"):
    dpg.add_item_hover_handler(callback=cc.set_time_to_show_tooltip)

#window_theme = themes.window_theme()
themes.launch_themes()

with dpg.window(label="Редактор обработки", show=False, pos=(0, 40), tag="plugins_window", 
width=827, height=476, min_size=(767, 350), on_close=lambda: dpg.hide_item("plugin_node_editor_registry")):
    dpg.add_spacer(height=5)
    with dpg.group(horizontal=True, horizontal_spacing=0):
        dpg.add_spacer(width=10)
        dpg.add_button(label="Добавить плагин", callback=inf.open_add_plugin_window)
        dpg.add_button(label="Просмотреть пресеты")
        dpg.add_button(label="Очистить редактор", enabled=False, tag="open_warning_clear_desk_button", 
        callback=inf.open_warning_clear_desk)
        dpg.add_button(label="Удалить данные", enabled=False, tag="delete_nodes_button", 
        callback=pm.delete_nodes_and_links)
        dpg.add_child_window(height=32, width=-199)
        with dpg.child_window(tag="apply_plugin_button", height=32, width=184):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Начать обработку", enabled=False, tag="begin_processing_button", callback=pm.apply_chain)
                dpg.add_image("button_separator")
                dpg.add_image_button("expand", tag="expand_modes_button", enabled=False, callback=inf.open_processing_modes_window)
                with dpg.tooltip(dpg.last_item(), tag="expand_tooltip"):
                    dpg.add_spacer(height=5)
                    with dpg.group(horizontal=True):
                        dpg.add_text("Добавьте хотя бы один объект для настройки режимов", wrap=250, indent=10)
                        dpg.bind_item_font(dpg.last_item(), "mini_italic")
                        dpg.add_spacer(width=10)
                    dpg.add_spacer(height=7)
        dpg.bind_item_theme("apply_plugin_button", themes.apply_plugins_button())
    #with dpg.group(horizontal=True, pos=(0, 30)):
    #    dpg.add_text("Плагин", indent=85)
    #    dpg.bind_item_font(dpg.last_item(), "micro_font")
    #    dpg.add_text("Файл", indent=320)
    #    dpg.bind_item_font(dpg.last_item(), "micro_font")
    #    dpg.add_text("Узлы и соединения", indent=482)
    #    dpg.bind_item_font(dpg.last_item(), "micro_font")
    dpg.add_spacer()
    with dpg.child_window(tag="plugin_node_editor_window", horizontal_scrollbar=True, height=-4):
        dpg.bind_item_font("plugin_node_editor_window", "node_items_font")
        with dpg.node_editor(tag="plugin_node_editor", width=2000, height=1000, 
        callback=pm.link_nodes, delink_callback=pm.delink_node):
            with dpg.node(label="Изображение", pos=(50, 400), tag="node_input_image"):
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_text("Исходное изображение")
                dpg.bind_item_theme("node_input_image", themes.node_input())
            with dpg.node(label="Вывод", pos=(850, 400), tag="node_output_image"):
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_text("Обработанное изображение")
                dpg.bind_item_theme("node_output_image", themes.node_output())
        dpg.bind_item_theme("plugin_node_editor_window", themes.node_editor_style())
    with dpg.child_window(height=32, pos=(-50, -50), width=32, tag="expand_window"):
        dpg.add_image_button("expand_to_full_white", callback=inf.open_plugins_window)
        dpg.bind_item_theme("expand_window", themes.expand_button_window())

dpg.bind_item_theme("plugins_window", "window_theme")
dpg.bind_item_handler_registry("plugins_window", "resize_node_plugins_window_handler")

# Окно добавления плагина
with dpg.window(label="Добавить плагин", show=False, pos=(300, 100), tag="add_plugins_window", 
width=320, height=427, modal=True):
    dpg.add_spacer(height=3)
    dpg.add_text("Избранное", indent=20)
    dpg.bind_item_font(dpg.last_item(), main_font)
    with dpg.group(tag="list_of_favorites", indent=10):
        dpg.bind_item_font("list_of_favorites", "mini_font")
        dpg.bind_item_theme("list_of_favorites", themes.plugin_window())
        dpg.add_text("Нет плагинов в избранном", indent=10, tag="no_plugins_in_favorites")
        dpg.bind_item_font("no_plugins_in_favorites", "mini_italic")
        dpg.add_text("В избранное можно добавлять не более 5 плагинов", indent=10, tag="no_more_5_plugins", 
        color=(249, 80, 80), show=False, wrap=290)
        for plugin_title in storage.plugins_titles:
            plugin_info = storage.plugins[storage.plugins_titles_to_names[plugin_title]]["info"]
            cc.add_plugin_item(plugin_title, plugin_info, in_favorites_list=True)
    dpg.add_spacer()
    dpg.add_color_button((228, 228, 228), indent=20, width=286, height=1, no_border=True, no_drag_drop=True)
    dpg.add_spacer(height=7)
    with dpg.group(horizontal=True):
        with dpg.child_window(tag="plugin_search_field", width=-46, height=32, no_scrollbar=True, indent=20):
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_spacer()
                    dpg.add_image("search_icon", indent=10)
                dpg.add_input_text(hint="Искать", height=20, pos=(44, 6), width=-1, 
                callback=lambda s, d: dpg.set_value("plugin_list_filter", d))
        with dpg.group():
            dpg.add_spacer()
            dpg.add_image("help_img")
    dpg.add_spacer(height=3)
    with dpg.child_window(tag="list_of_plugins", indent=10, width=0, height=-10):
        dpg.bind_item_font("list_of_plugins", "mini_font")
        dpg.bind_item_theme("list_of_plugins", themes.plugin_window())
        with dpg.filter_set(tag="plugin_list_filter"):
            for plugin_title in storage.plugins_titles:
                plugin_info = storage.plugins[storage.plugins_titles_to_names[plugin_title]]["info"]
                cc.add_plugin_item(plugin_title, plugin_info)
    dpg.bind_item_theme("plugin_search_field", themes.search_field())

dpg.bind_item_theme("add_plugins_window", "window_theme")

with dpg.window(label="Предупреждение", show=False, pos=(0, 0), tag="warning_clear_desk", 
width=342, height=142, no_title_bar=True, no_resize=True, no_move=True, modal=True):
    dpg.add_spacer(height=3)
    dpg.add_text("Вы уверены?", indent=20)
    dpg.bind_item_font(dpg.last_item(), "warning_title")
    dpg.add_text("Очистка редактора приведёт к удалению всех плагинов и связей между ними.", wrap=320, indent=20)
    dpg.add_spacer(height=2)
    with dpg.group(horizontal=True, indent=170):
        dpg.add_button(label="Удалить", tag="clear_desk_button", callback=pm.clear_desk)
        dpg.bind_item_theme("clear_desk_button", themes.delete_button())
        dpg.bind_item_font("clear_desk_button", "button_label")
        dpg.add_button(label="Отмена", tag="cancel_clear_button", callback=lambda: dpg.hide_item("warning_clear_desk"))
        dpg.bind_item_theme("cancel_clear_button", themes.cancel_button())

dpg.bind_item_theme("warning_clear_desk", "window_theme")

with dpg.window(label="Режимы обработки", show=False, tag="modes_of_processing_window", 
width=261, height=285, no_title_bar=True, no_resize=True, no_move=True):
    with dpg.child_window(width=259, height=283, tag="modes_of_processing"):
        dpg.add_spacer(height=5)
        #dpg.add_text("КАДРЫ", indent=105)
        #dpg.bind_item_font(dpg.last_item(), "micro_font")
        #dpg.add_spacer(height=3)
        cc.plugin_node_menu_item("Только текущий кадр", selected=True, tag="one_frame", 
        all_frames=False, group="frames")
        cc.plugin_node_menu_item("Все кадры", tag="all_frames", all_frames=True, group="frames")
        dpg.add_spacer(height=3)
        dpg.add_color_button((228, 228, 228), indent=10, width=241, height=1, no_border=True, no_drag_drop=True)
        dpg.add_spacer(height=3)
        #dpg.add_text("ФАЙЛЫ", indent=105)
        #dpg.bind_item_font(dpg.last_item(), "micro_font")
        cc.plugin_node_menu_item("Только текущий файл", selected=True, tag="one_file_mode", 
        mode=PROCESS_MODES.one, group="modes")
        cc.plugin_node_menu_item("Все файлы", tag="all_files_mode", mode=PROCESS_MODES.all_files, group="modes")
        cc.plugin_node_menu_item("Определённые файлы...", tag="several_files_mode", mode=PROCESS_MODES.several, group="modes")
        cc.plugin_node_menu_item("Новые файлы", tag="new_files_mode", mode=PROCESS_MODES.new, 
        group="modes", disabled=True)
        cc.plugin_node_menu_item("Ранее обработанные файлы", tag="earlier_mode", mode=PROCESS_MODES.earlier, 
        group="modes", disabled=True)
        dpg.add_spacer(height=3)
        #dpg.add_spacer(height=3)
        #with dpg.group(horizontal=True, indent=10):
        #    dpg.add_checkbox(default_value=True)
        #    dpg.add_text("Не обрабатывать файлы со статусом \"Актуальный\"", wrap=200)
        #    dpg.bind_item_font(dpg.last_item(), "mini_font")

dpg.bind_item_theme("modes_of_processing_window", themes.window_shadow())

#! окно загрузки изображений из URL
with dpg.window(label="Добавить URL", show=False, width=600, height=400, tag="add_urls_window", min_size=(350, 255)):
    with dpg.group(indent=10):
        dpg.add_spacer(height=5)
        dpg.add_text("Добавьте URL (новый URL с новой строки):")
        dpg.add_input_text(multiline=True, tag="urls", width=-10, height=-48)
        dpg.add_spacer()
        with dpg.group(horizontal=True):
            dpg.add_child_window(width=-267)
            dpg.add_button(label="Добавить файлы из интернета", callback=fo.open_objects, user_data=OBJECT_TYPES.url)
            dpg.bind_item_theme(dpg.last_item(), themes.outline_button())

dpg.bind_item_theme("add_urls_window", "window_theme")

#! окно подключения к камере
with dpg.window(label="Добавить камеру", show=False, width=600, height=204, tag="connect_to_camera_window", 
min_size=(400, 204), max_size=(800, 204), user_data={"error": False}):
    with dpg.group(indent=10):
        dpg.add_spacer(height=5)
        dpg.add_radio_button(["Веб-камера", "IP-камера"], horizontal=True, callback=inf.change_camera_fields, 
        tag="type_of_camera", default_value="Веб-камера")
        dpg.add_spacer(height=2)
        with dpg.group(tag="web-camera_group", show=True):
            with dpg.group(horizontal=True, horizontal_spacing=3):
                dpg.add_text("Номер потока с нуля")
                dpg.add_spacer(width=4)
                dpg.add_input_int(tag="camera_number", width=-10, step=1, min_value=0)
        with dpg.group(tag="IP-camera_group", show=False):
            with dpg.group(horizontal=True, horizontal_spacing=3):
                dpg.add_text("Адрес IP-камеры")
                dpg.add_text("*", color=(249, 80, 80))
                dpg.add_spacer(width=4)
                dpg.add_input_text(tag="camera_url", width=-10, 
                callback=lambda: dpg.configure_item("add_camera_button", enabled=dpg.get_value("camera_url") != ""))
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text("Пользователь", tag="camera_user")
                    dpg.add_spacer(width=20)
                    dpg.add_input_text(width=-10)
                with dpg.group(horizontal=True):
                    dpg.add_text("Пароль", tag="camera_password")
                    dpg.add_spacer(width=68)
                    dpg.add_input_text(width=-10, password=True)
        dpg.add_spacer()
        with dpg.group(tag="error_connect_to_camera", show=False, horizontal=True):
            dpg.add_text("Ошибка при подключении к камере", color=(249, 80, 80))
            dpg.add_image("help_img")
        dpg.add_checkbox(label="Переключиться на добавленную камеру", default_value=True, 
        tag="change_after_connect_to_camera", enabled=False)
        dpg.add_spacer()
        with dpg.group(horizontal=True):
            dpg.add_child_window(width=-168) # 185
            dpg.add_button(label="Добавить камеру", callback=fo.open_objects, user_data=OBJECT_TYPES.stream, 
            tag="add_camera_button")
            dpg.bind_item_theme("add_camera_button", themes.outline_button())

dpg.bind_item_theme("connect_to_camera_window", "window_theme")

#! диалоговое окно открытия файлов
with dpg.file_dialog(label="Открыть объекты", callback=fo.open_objects, directory_selector=False,
show=False, tag="pc_file_dialog", user_data=OBJECT_TYPES.file, default_path="D:", width=800, height=600):
    dpg.add_file_extension("Все объекты (*.jpg *.jpeg *.png *.gif *.avi *.mp4 *.ogv *.mov) \
    {.jpg,.jpeg,.png,.gif,.avi,.mp4,.ogv,.mov}")
    dpg.add_file_extension("Изображения (*.jpg *.jpeg *.png *.gif){.jpg,.jpeg,.png,.gif}")
    dpg.add_file_extension("Видео (*.avi *.mp4 *.ogv *.mov){.avi,.mp4,.ogv,.mov}")
    dpg.add_file_extension(".jpg", color=(155, 213, 255, 255), custom_text="[Image]")
    dpg.add_file_extension(".jpeg", color=(155, 213, 255, 255), custom_text="[Image]")
    dpg.add_file_extension(".png", color=(155, 213, 255, 255), custom_text="[Image]")
    dpg.add_file_extension(".gif", color=(155, 213, 255, 255), custom_text="[Image]")
    dpg.add_file_extension(".avi", color=(167, 255, 117, 255), custom_text="[Video]")
    dpg.add_file_extension(".mp4", color=(167, 255, 117, 255), custom_text="[Video]")
    dpg.add_file_extension(".ogv", color=(167, 255, 117, 255), custom_text="[Video]")
    dpg.add_file_extension(".mov", color=(167, 255, 117, 255), custom_text="[Video]")

# диалоговое окно открытия файлов из папки
with dpg.file_dialog(label="Открыть папку", callback=fo.open_folder, show=False, tag="pc_folder_dialog", 
user_data=OBJECT_TYPES.file, default_path="D:", width=800, height=600) as pc_folder_dialog:
    dpg.add_text("Виды файлов:")
    dpg.add_combo(items=["Изображения + Видео", "Изображения", "Видео"], default_value="Изображения + Видео", tag="kinds_of_files")
    dpg.bind_item_theme("pc_folder_dialog", themes.get_menu_theme())

# диалоговое окно сохранения файлов
with dpg.file_dialog(label="Сохранить все объекты", directory_selector=True,
show=False, tag="save_files_dialog", width=800, height=600):
    dpg.add_text("Сохранить под именами:")
    dpg.add_radio_button(items=("Исходные имена", "Программное имя"), tag="set_program_name",
    default_value="Исходные имена", callback=inf.set_group_program_name_visible)
    with dpg.group(tag="program_text_field", show=False):
        dpg.add_text("Программное имя объекта без расширения. Символ $ - заменяется на цифру. Наличие символа $ обязательно.")
        dpg.add_text("Изображения с одинаковым именем перезаписываются.", color=(255, 0, 0, 255))
        dpg.add_input_text(tag="program_name")
    dpg.add_text("Сохранять изображения в формате:")
    dpg.add_radio_button(items=("png", "jpg"), default_value="png", tag="image_format")
    dpg.add_text("Сохранять видео в формате:")
    dpg.add_radio_button(items=("mp4", "avi"), default_value="mp4", tag="video_format")
    dpg.add_separator()
    dpg.add_checkbox(label="Закрыть все файлы", default_value=True, tag="close_all_files")

#! диалоговое окно открытия файлов (для настроек плагинов)
with dpg.file_dialog(label="Открыть объекты", callback=pm.file_set_path, directory_selector=False, show=False, 
tag="pc_file_plugin_dialog", default_path="D:", file_count=1, width=800, height=600):
    dpg.add_file_extension(".*")

#! диалоговое окно открытия JSON-файлов
with dpg.file_dialog(label="Открыть цепочку плагинов из файла", callback=pm.open_chain_from_file, 
directory_selector=False, show=False, default_path="E:/opencv", file_count=1, width=800, height=600, tag="json_open_dialog"):
    dpg.add_file_extension(".json", color=(255, 150, 150, 255), custom_text="[Configuration]")

#! главное окно
with dpg.window(tag="objects_window"):
    dpg.bind_font(main_font)
    with dpg.group(horizontal=True, tag="main_menu", horizontal_spacing=0):
        dpg.add_spacer(width=10)
        with dpg.child_window(label="Файл", tag="file_button", height=32, width=74):
            dpg.add_spacer(height=2)
            with dpg.group(horizontal=True, horizontal_spacing=5):
                dpg.add_text("Файл")
                with dpg.group():
                    dpg.add_spacer(height=5)
                    dpg.add_image("expand")
        dpg.bind_item_theme("file_button", "default_button_theme")
        dpg.bind_item_handler_registry("file_button", file_button_registry)

        dpg.add_button(label="Обработка", callback=inf.open_plugins_window)

        with dpg.child_window(label="Приложение", tag="app_button", height=32, width=130):
            dpg.add_spacer(height=2)
            with dpg.group(horizontal=True, horizontal_spacing=5):
                dpg.add_text("Приложение")
                with dpg.group():
                    dpg.add_spacer(height=5)
                    dpg.add_image("expand")
        dpg.bind_item_theme("app_button", "default_button_theme")
        dpg.bind_item_handler_registry("app_button", app_button_registry)

        with dpg.child_window(label="Информация", tag="information_button", height=32, width=116):
            dpg.add_spacer(height=2)
            with dpg.group(horizontal=True, horizontal_spacing=1):
                dpg.add_text("Информация", color=(194, 194, 194), tag="information_button_text")
                dpg.add_image("red_point", show=False, tag="red_point_image")
        dpg.bind_item_theme("information_button", "default_button_theme")
        dpg.bind_item_handler_registry("information_button", information_button_registry)
        dpg.add_spacer(width=10)
        dpg.add_image("vertical_separator")
        dpg.add_spacer(width=10)

        with dpg.child_window(label="Добавить файлы", tag="add_file_buttons", height=32, width=128):
            with dpg.group(horizontal=True, horizontal_spacing=0):
                dpg.add_image_button("add_image", callback=lambda: dpg.show_item("pc_file_dialog"))
                dpg.bind_item_theme(dpg.last_item(), themes.green_button_square_theme())
                dpg.add_image_button("add_folder", callback=lambda: dpg.show_item("pc_folder_dialog"))
                dpg.bind_item_theme(dpg.last_item(), themes.green_button_square_theme())
                dpg.add_image_button("add_from_internet", callback=lambda: inf.open_window_at_center("add_urls_window"))
                dpg.bind_item_theme(dpg.last_item(), themes.green_button_square_theme())
                dpg.add_image_button("add_ip_camera", callback=lambda: inf.open_window_at_center("connect_to_camera_window"))
                dpg.bind_item_theme(dpg.last_item(), themes.green_button_square_theme())
        dpg.bind_item_theme("add_file_buttons", themes.group_buttons_theme())
        dpg.add_spacer(width=10)
        dpg.add_image("vertical_separator")
        dpg.add_spacer(width=10)

        with dpg.child_window(label="Переключить файлы", tag="manipulate_file_buttons", height=32, width=96):
            with dpg.group(horizontal=True, horizontal_spacing=0):
                dpg.add_image_button("prev_file_inactive", tag="prev_file_button", enabled=False)
                dpg.bind_item_theme(dpg.last_item(), themes.blue_button_square_theme())
                dpg.add_image_button("more_files_inactive", tag="more_files_button", enabled=False, 
                callback=inf.open_file_explorer)
                dpg.bind_item_theme(dpg.last_item(), themes.blue_button_square_theme())
                dpg.add_image_button("next_file_inactive", tag="next_file_button", enabled=False)
                dpg.bind_item_theme(dpg.last_item(), themes.blue_button_square_theme())
        dpg.bind_item_theme("manipulate_file_buttons", themes.group_buttons_theme())

        dpg.add_spacer(width=10)
        dpg.add_image("vertical_separator")
        dpg.add_spacer(width=10)
        dpg.add_image_button("close_image_inactive", tag="close_files_button", enabled=False)
        dpg.bind_item_theme("close_files_button", "close_button_theme")
        dpg.add_spacer(width=10)
        dpg.add_image_button("delete_temp_files", tag="close_and_delete_temp_files", enabled=False, 
        show=False, callback=lambda: dpg.show_item("warning_of_delete_window"))
        dpg.bind_item_theme("close_and_delete_temp_files", "close_button_theme")
        dpg.add_spacer(width=10)
        dpg.add_child_window(height=32, width=-128)
        dpg.bind_item_theme(dpg.last_item(), themes.white_background())
        dpg.add_spacer(width=10)

        with dpg.child_window(label="Изменить размер изображения", tag="zoom", height=32, width=109, show=False):
            with dpg.group(horizontal=True, horizontal_spacing=0):
                dpg.add_image_button("zoom_plus", callback=lambda: pv.zoom("plus"), tag="plus_zoom_button")
                dpg.bind_item_theme(dpg.last_item(), themes.blue_button_square_theme())
                dpg.add_image_button("zoom_minus", callback=lambda: pv.zoom("minus"), tag="minus_zoom_button")
                dpg.bind_item_theme(dpg.last_item(), themes.blue_button_square_theme())
                dpg.add_button(label="100%", callback=lambda: pv.zoom("100"), tag="100_zoom_button")
                dpg.bind_item_theme(dpg.last_item(), themes.zoom_ind_theme())
        dpg.bind_item_theme("zoom", themes.group_buttons_theme())

    with dpg.group(show=False, tag="group_of_objects"):
        #dpg.add_text("В демо-версии можно загружать ролики не длиннее 1 минуты!", tag="limit_1_minute", color=(249, 80, 80), indent=20)
        with dpg.child_window(horizontal_scrollbar=True, tag="main_image_child_window", show=False):
            dpg.add_image("main_image", tag="main_image_desk")
        dpg.bind_item_theme("group_of_objects", themes.thin_scrollbar())
        dpg.bind_item_handler_registry("main_image_child_window", "image_handler_registry")

    with dpg.child_window(tag="hello_splash", height=-32):
        with dpg.group(indent=340, tag="indent_group"):
            dpg.add_spacer(height=160, tag="vertical_splash_spacer")
            dpg.add_text("Приветствуем в программе RoadX!", indent=110)
            dpg.bind_item_font(dpg.last_item(), "title")
            dpg.add_spacer(height=10)
            dpg.add_image("app_splash", indent=210)
            dpg.add_spacer(height=10)
            dpg.add_text("Для начала работы откройте объект (зелёные кнопки или меню \"Файл\")")
            dpg.add_spacer(height=10)
            dpg.add_text("Для разблокировки всех возможностей активируйте полную версию", color=(249, 80, 80), indent=15, show=False)
    dpg.bind_item_theme("hello_splash", themes.splash_window())

    ### Строка с информацией (или с загрузкой)
    with dpg.child_window(tag="status_bar", height=28):
        dpg.add_spacer()
        dpg.add_text("", indent=20, tag="status_bar_info")
        with dpg.group(show=False, tag="state_of_loading", horizontal=True):
            dpg.add_spacer(width=2)
            dpg.add_loading_indicator(speed=2, style=1, radius=1, tag="loading_indicator")
            dpg.add_text("Загрузка плагина", tag="text_of_loading")
            dpg.add_progress_bar(tag="progress_bar", width=300, show=False)
            dpg.add_spacer(width=2)
            dpg.add_text("0:00", tag="time_from_begin")
            with dpg.group(tag="time_evaluation", horizontal=True):
                dpg.add_text(" / ")
                dpg.add_text("Оценивается...", tag="possible_time_ending")

#! Видеоплеер
with dpg.window(label="Видеоплеер", pos=(350, 500), no_move=True, no_resize=True, no_scrollbar=True,
no_title_bar=True, width=560, height=90, tag="video_player_window", user_data={"opacity": 0}, show=False,
no_open_over_existing_popup=True):
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True, tag="player_buttons"):
        dpg.add_image_button("skip_backward", tag="skip_backward_button", callback=pv.go_to_begin)
        dpg.add_image_button("prev_frame", tag="prev_frame_button", callback=pv.go_to_prev_frame)
        dpg.add_image_button("play", tag="play_button", callback=pv.toggle_play)
        dpg.add_image_button("next_frame", tag="next_frame_button", callback=pv.go_to_next_frame)
        dpg.add_image_button("skip_forward", tag="skip_forward_button", callback=pv.go_to_end)
    with dpg.group(horizontal=True):
        dpg.add_image_button("locked", tag="lock_button")
        dpg.bind_item_theme("lock_button", themes.lock_button())
        dpg.add_text("0:00", color=(255, 255, 255), tag="time_video_from_begin")
        dpg.add_spacer()
        with dpg.group():
            dpg.add_spacer(height=8)
            dpg.add_child_window(width=420, height=9, tag="player_pan")
            dpg.bind_item_theme("player_pan", themes.player_pan())
            dpg.bind_item_handler_registry("player_pan", "pan_handler_registry")
        dpg.add_spacer()
        dpg.add_text("0:00", color=(255, 255, 255), tag="video_duration")
    dpg.add_child_window(width=1, height=9, tag="player_progress", pos=(98, 70))
    dpg.bind_item_theme("player_progress", themes.player_progress())
    dpg.bind_item_handler_registry("player_progress", "pan_handler_registry")
dpg.bind_item_theme("video_player_window", themes.player_window())

###! Раскрывающиеся окна "Файл" и "Приложение"
with dpg.window(label="Файл", show=False, pos=(8, 46), no_title_bar=True, no_move=True, 
no_resize=True, tag="file_menu_window", width=293, height=388):
    with dpg.child_window(width=291, height=386, tag="file_menu"):
        dpg.add_spacer(height=5)
        cc.add_menu_item("Открыть файл", shortcut="Ctrl + O", spacer_width=77, 
        width=300, tag="open_file_menu_item", callback=lambda: dpg.show_item("pc_file_dialog"))
        cc.add_menu_item("Открыть папку", shortcut="Ctrl + F", spacer_width=75, 
        width=300, tag="open_folder_menu_item", callback=lambda: dpg.show_item("pc_folder_dialog"))
        cc.add_menu_item("Загрузить из интернета", width=300, callback=lambda: inf.open_window_at_center("add_urls_window"),
        tag="add_from_internet_menu_item")
        cc.add_menu_item("Подключиться к IP-камере", width=300, tag="connect_to_camera_menu_item", 
        callback=lambda: inf.open_window_at_center("connect_to_camera_window"))
        dpg.add_color_button((228, 228, 228), indent=20, width=253, height=1, no_border=True, no_drag_drop=True)
        cc.add_menu_item("Сохранить изображение / кадр",
        tag="save_image_menu_item", disabled=True, width=293)
        cc.add_menu_item("Сохранить все кадры", tag="save_all_frames_menu_item", disabled=True, width=293)
        cc.add_menu_item("Сохранить видео", tag="save_video_menu_item", disabled=True, width=293)
        cc.add_menu_item("Сохранить все изображения", "file_menu",
        tag="save_all_images_menu_item", disabled=True, width=293)
        dpg.add_color_button((228, 228, 228), indent=20, width=253, height=1, no_border=True, no_drag_drop=True)
        cc.add_menu_item("Закрыть", spacer_width=123, shortcut="Ctrl + C",
        tag="close_menu_item", disabled=True, width=300, callback=fo.close_object)
        cc.add_menu_item("Закрыть всё", spacer_width=48, shortcut="Ctrl + Shift + C",
        tag="close_all_menu_item", disabled=True, width=300, callback=fo.close_all_objects)
dpg.bind_item_theme("file_menu_window", themes.window_shadow())

with dpg.window(label="Приложение", show=False, pos=(181, 48), no_title_bar=True, no_move=True, 
no_resize=True, tag="app_menu_window", width=224, height=160):
    with dpg.child_window(width=222, height=158, tag="app_menu"):
        dpg.add_spacer(height=5)
        cc.add_menu_item("Настройки", spacer_width=33, shortcut="Ctrl + N",
        tag="settings_menu_item", width=222, callback=lambda: dpg.show_item("settings_of_the_program"))
        cc.add_menu_item("Горячие клавиши", tag="hotkeys_menu_item", width=222, 
        callback=lambda: dpg.show_item("hotkeys_window"))
        cc.add_menu_item("Лицензия и демо-версия", tag="license_menu_item", width=222)
        cc.add_menu_item("О программе", tag="about_program_menu_item", width=222, 
        callback=lambda: dpg.show_item("info_about_the_program"))
dpg.bind_item_theme("app_menu_window", themes.window_shadow())

#! Окно с предупреждением
with dpg.window(no_title_bar=True, width=210, height=100, pos=(726, 48), no_resize=True, 
no_move=True, tag="warning_of_delete_window", show=False):
    with dpg.child_window(width=208, height=98, tag="warning_of_delete"):
        dpg.add_spacer(height=7)
        dpg.add_text("Временные файлы будут удалены, а файл закрыт.", indent=10, wrap=198)
        dpg.add_spacer(height=3)
        with dpg.group(horizontal=True, indent=10):
            dpg.add_button(label="Удалить", tag="delete_temp_files_button", callback=pv.delete_temp_folders_and_close_video)
            dpg.bind_item_theme("delete_temp_files_button", themes.delete_button())
            dpg.bind_item_font("delete_temp_files_button", "button_label")
            dpg.add_button(label="Отмена", tag="cancel_button", callback=lambda: dpg.hide_item("warning_of_delete_window"))
            dpg.bind_item_theme("cancel_button", themes.cancel_button())
dpg.bind_item_theme("warning_of_delete_window", themes.window_shadow())

with dpg.window(label="Менеджер файлов", width=440, height=420, pos=(200, 100), 
tag="file_explorer_window", show=False, min_size=(288, 252), delay_search=True):
    dpg.add_spacer(height=7)
    with dpg.child_window(tag="search_field", width=-10, height=32, no_scrollbar=True, indent=10):
        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_spacer()
                dpg.add_image("search_icon", indent=10)
            dpg.add_input_text(hint="Искать", height=20, pos=(44, 6), width=-1,
            callback=lambda s, d: dpg.set_value("file_filter_container", d), tag="search_field_input")
    dpg.bind_item_theme("search_field", themes.search_field())
    dpg.add_spacer(height=4)
    with dpg.child_window(height=-58, tag="file_container", indent=10):
        dpg.add_filter_set(tag="file_filter_container")
    dpg.bind_item_theme("file_container", themes.thin_scrollbar())
    dpg.add_spacer(height=7)
    with dpg.group(horizontal=True):
        with dpg.group(indent=20):
            dpg.add_spacer()
            dpg.add_image("help_img")
        dpg.add_spacer(width=64, tag="spacer_between_help_and_close_button")
        with dpg.child_window(width=194, height=33, tag="close_all_files_button"):
            with dpg.group(horizontal=True):
                dpg.add_image("circle_close")
                dpg.add_text("Закрыть все файлы", color=(253, 62, 62), pos=(40, 5))
    dpg.bind_item_theme("close_all_files_button", "close_all_objects_button_default")
    dpg.bind_item_handler_registry("close_all_files_button", "close_all_files_button_registry")
dpg.bind_item_handler_registry("file_explorer_window", "resize_window_handler")

dpg.bind_item_theme("file_explorer_window", "window_theme")

#! окно с информацией в результате обработки
with dpg.window(label="Информация, полученная в результате обработки", show=False, pos=(100, 100), 
no_resize=True, tag="information_window", width=897, height=423):
    with dpg.group(tag="information_tab_bar"):
        with dpg.tab_bar():
            with dpg.tab(label="Видео", indent=10, tag="information_video_tab"):
                dpg.add_text("Графики")
                dpg.bind_item_font(dpg.last_item(), "tab_title")
                dpg.add_color_button((64, 149, 227), width=46, height=3, no_drag_drop=True, 
                no_border=True, pos=(10, 69))
                with dpg.child_window(horizontal_scrollbar=True):
                    dpg.add_text('В настоящее время здесь ничего нет', tag="no_plots_text")
                    dpg.bind_item_font("no_plots_text", "mini_italic")
                    dpg.add_group(horizontal=True, tag="video_plots_group")
                    dpg.add_spacer()
                    with dpg.group(horizontal=True, tag="plot_combo_group", show=False):
                        with dpg.group():
                            dpg.add_spacer()
                            dpg.add_text("Раскрыть на полный экран:")
                        dpg.add_combo(["(Нет)"], tag="plots_combo", default_value="(Нет)", 
                        width=350, callback=inf.open_plugin_window)
                        dpg.bind_item_theme("plots_combo", themes.combo_style())
            with dpg.tab(label="Изображение", indent=10, tag="information_image_tab"):
                dpg.add_text("Информация от плагинов")
                dpg.bind_item_font(dpg.last_item(), "tab_title")
                dpg.add_color_button((64, 149, 227), width=102, height=3, no_drag_drop=True, 
                no_border=True, pos=(82, 69))
        dpg.bind_item_theme("information_tab_bar", themes.tabs_outline())

dpg.bind_item_theme("information_window", "window_theme")

with dpg.window(label="Предупреждение", show=False, tag="please_connect_flash", pos=(400, 300), no_resize=True, no_collapse=True):
    dpg.add_text("Пожалуйста, вставьте электронный ключ в компьютер!")

with dpg.window(label="Ограничения в демо-версии", show=False, tag="demo_version_description", pos=(400, 300), 
no_resize=True, width=430, no_collapse=True):
    dpg.add_text("Нельзя загрузить изображения из интернета", bullet=True)
    dpg.add_text("Максимальная длительность видео — 1 минута", bullet=True)
    dpg.add_text("Максимальная длительность цепочки — 5 плагинов", bullet=True)

with dpg.window(label="Информация о файле ключа", show=False, tag="info_about_key", 
pos=(400, 300), width=560, no_resize=True, no_collapse=True):
    dpg.add_text("", tag="letter_of_key_text")
    dpg.add_text("", tag="info_about_key_text", wrap=550)

with dpg.window(label="Выходные данные ключа", show=False, tag="params_of_key", pos=(300, 30), width=720, 
height=600, no_collapse=True):
    dpg.add_text("", tag="params_of_key_text")

with dpg.window(label="Проверка файла ключа", show=False, tag="key_check", 
pos=(300, 50), width=300, height=106, no_collapse=True, no_resize=True):
    dpg.add_text("Ключ валиден", tag="key_validity", color=(70, 204, 40))
    dpg.add_text("Срок действия не истёк", tag="key_expiration", color=(70, 204, 40), show=False)

with dpg.window(label="Журнал проверок", tag="journal_of_checks", show=False, height=500):
    dpg.add_text("", tag="journal")
    dpg.add_button(label="Очистить журнал", callback=usbkey.clear_journal)

with dpg.window(label="Настройки программы", show=False, tag="settings_of_the_program", no_resize=True, pos=(300, 100),
on_close=lambda: dpg.hide_item("settings_of_program_have_saved")):
    with dpg.group(horizontal=True):
        dpg.add_text("Качество изображений:")
        dpg.add_slider_int(min_value=0, max_value=100, 
        default_value=storage.program_settings["quality_of_pictures"], width=200, tag="quality_of_pictures")
    dpg.add_checkbox(label="Автоматически обрабатывать изображение при изменении цепочки плагинов", 
    default_value=storage.program_settings["auto_apply"], tag="auto_process_images")
    dpg.add_checkbox(label="Звуковое оповещение по окончании обработки видео", 
    default_value=storage.program_settings["send_signal"], tag="send_beep")
    dpg.add_checkbox(label="Отображать результаты обработки кадра", 
    default_value=storage.program_settings["display_image_process"], tag="display_image_process")
    dpg.add_checkbox(label="Отображать результаты обработки видео", 
    default_value=storage.program_settings["display_video_process"], tag="display_video_process")
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Сохранить настройки", callback=inf.save_program_settings)
        dpg.add_text("Настройки сохранены", show=False, tag="settings_of_program_have_saved")

with dpg.window(label="О программе", show=False, tag="info_about_the_program", no_resize=True, pos=(300, 100)):
    dpg.add_text("Программа RoadX")
    dpg.add_text("Платформа: Desktop-Crossplatform (Windows, Linux, MacOS)")
    dpg.add_text("Версия 0.3.1")
    with dpg.group(horizontal=True):
        dpg.add_text("Автор: Истигечев Борис (https://github.com/Neoclassic-alt)")
        dpg.add_button(label="Копировать URL", callback=lambda: clipboard.copy("https://github.com/Neoclassic-alt"))
    with dpg.group(horizontal=True):
        dpg.add_text("Организация: Сибирский государственный университет науки и технологий (sibsau.ru)")
        dpg.add_button(label="Копировать URL", callback=lambda: clipboard.copy("https://sibsau.ru"))
    dpg.add_text("Краткое название организации: СибГУ им. Решетнёва")
    dpg.add_text("Последнее изменение программы: 06.01.2022 от Р. Х.")
    dpg.add_spacer(height=10)
    dpg.add_text("Istigechev Boris (C) 2022")

with dpg.window(label="Горячие клавиши", show=False, tag="hotkeys_window", no_resize=True, no_collapse=True, 
width=310, pos=(300, 200)):
    dpg.add_text("N — открытие окна настроек", bullet=True)
    dpg.add_text("P — открытие окна плагинов", bullet=True)
    dpg.add_text("A — применить цепочку плагинов", bullet=True)

dpg.add_window(label="График плагина", show=False, autosize=True, no_resize=True, tag="plugin_window")
dpg.bind_item_theme("plugin_window", themes.window_rounding())

dpg.bind_theme(themes.get_theme())
dpg.bind_item_theme("objects_window", themes.null_padding_primary_window())

#dpg.show_style_editor()
#dpg.show_debug()
#dpg.show_metrics()
warnings.filterwarnings("ignore") # игнорирование предупреждений

dpg.create_viewport(title='RoadX Watching System', width=1000, height=600, x_pos=350, y_pos=150)
dpg.set_viewport_resize_callback(callback=inf.resize_viewport)

dpg.set_viewport_small_icon("assets/images/app.ico")
dpg.set_viewport_large_icon("assets/images/app.ico")

dpg.setup_dearpygui()
dpg.set_primary_window("objects_window", True)
dpg.show_viewport()
#dpg.toggle_viewport_fullscreen()
usbkey.try_limit()

while dpg.is_dearpygui_running():
    if dpg.get_frame_count() % 50 == 0:
        check_connect()
    if storage.is_playing:
        storage.next_current_frame()
        pv.open_frame(storage.current_frame)
        fps = round(1/dpg.get_delta_time(), 2)
        #if dpg.get_frame_count() % 20 == 0:
            #dpg.set_value("speed_frames_text", f"{fps} кадров/сек")
        # для соответствия воспроизведения частоты кадров видео и частоты обновления экрана
        time.sleep(max(0.0, 1/storage.frame_rate - dpg.get_delta_time()))
    if not storage.current_object is None and storage.current_object["type"] == OBJECT_TYPES.video \
        and not dpg.get_item_state("plugins_window")["visible"] and not storage.crosshair[0]:
        storage.add_to_video_timer(dpg.get_delta_time())

        if storage.video_timer < 2.5 and dpg.get_item_user_data("video_player_window")["opacity"] < 255:
            dpg.show_item("video_player_window")
            dpg.set_item_user_data("video_player_window", {"opacity": dpg.get_item_user_data("video_player_window")["opacity"] + 20})
            if dpg.get_item_user_data("video_player_window")["opacity"] > 255:
                dpg.set_item_user_data("video_player_window", {"opacity": 255})
            
        if storage.video_timer > 2.5 and dpg.get_item_user_data("video_player_window")["opacity"] > 0:
            dpg.set_item_user_data("video_player_window", {"opacity": dpg.get_item_user_data("video_player_window")["opacity"] - 20})
            if dpg.get_item_user_data("video_player_window")["opacity"] < 0:
                dpg.set_item_user_data("video_player_window", {"opacity": 0})
                dpg.hide_item("video_player_window")

        opacity = dpg.get_item_user_data("video_player_window")["opacity"]
        inf.apply_opacity_to_video_player(opacity)

    if dpg.get_item_state("plugins_window")["visible"] or storage.crosshair[0]:
        dpg.hide_item("video_player_window")

    if storage.is_processing:
        storage.add_to_process_timer(dpg.get_delta_time())
        minutes = storage.processed_time // 60
        seconds = storage.processed_time % 60
        dpg.set_value("time_from_begin", "{0:02d}:{1:02d}".format(int(minutes), int(seconds)))
        if storage.is_divisible and dpg.get_frame_count() % 30 == 0:
            if storage.processed_time > 6 and storage.part_of_process > 0.02:
                remaining_time = (1 / storage.part_of_process - 1) * storage.processed_time
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                dpg.set_value("possible_time_ending", "{0:02d}:{1:02d}".format(int(minutes), int(seconds)))
            else:
                dpg.set_value("possible_time_ending", "Оценивается...")

    if storage.is_camera_playing:
        #! НЕ РАБОТАЕТ С ВИРТУАЛЬНЫМИ КАМЕРАМИ!
        ret, frame = storage.caption.read()
        print(frame.shape)
        pv.change_texture(frame)
        print(dpg.get_delta_time())
    elif not storage.caption is None:
        storage.caption.release()
        storage.set_value(keys.CAPTION, None)

    dpg.render_dearpygui_frame()

dpg.destroy_context()
