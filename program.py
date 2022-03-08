from subprocess import call
import dearpygui.dearpygui as dpg
import json
from components.functions import AppInfo as app_info
from components.storage import OBJECT_TYPES
import components.key_module as key_module
import components.plugin_manager as pm
from components.storage import storage, keys
import components.styling as themes
import components.photo_video as pv
import components.file_operations as fo
import warnings
import pyperclip as clipboard
import time
import webbrowser

# загрузка модулей
storage.set_value(keys.PLUGINS, pm.load_plugins())

# связываем заголовок плагина с его именем для нужд интерфейса
pm.set_titles_to_names()

def print_data(sender, app_data, user_data):
    print(sender, app_data, user_data)

# загрузка сохранённых настроек плагинов из файла settings.json
with open("C:\ProgramData\cv_experiments\settings.json", "r", encoding='utf-8') as json_file:
    json_load = json.load(json_file)
    storage.set_value(keys.PLUGINS_SETTINGS, json_load.copy())
    storage.set_value(keys.PLUGINS_PRIOR_SETTINGS, json_load.copy())

for key in storage.plugins:
    if storage.plugins_settings.get(key) is None:
        storage.set_plugin_settings(key, {})
    interface = storage.plugins[key]['interface']
    if not interface is None:
        for field in interface:
            if storage.plugins_settings[key].get(field['var']) is None and field['type'] != "file":
                value = field.get('default_value')
                if value is None:
                    if field['type'] == "checkbox":
                        storage.set_plugin_settings_field(key, field['var'], False)
                    if field['type'] == "input":
                        storage.set_plugin_settings_field(key, field['var'], '')
                    if field['type'] == "numbers":
                        storage.set_plugin_settings_field(key, field['var'],
                        field['settings'].get('min') if field['settings'].get('min') else 0)
                    if field['type'] == 'slider':
                        storage.set_plugin_settings_field(key, field['var'], 0)
                    if field['type'] == '2d-point':
                        storage.set_plugin_settings_field(key, field['var'], [0, 0])
                storage.set_plugin_settings_field(key, field['var'], field.get('default_value'))

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

# сохраняем новые настройки и плагины, если они есть
with open("C:\ProgramData\cv_experiments\settings.json", "w") as write_file:
    json.dump(storage.plugins_settings, write_file, indent=4, ensure_ascii=True)

dpg.create_context()

with dpg.font_registry():
    with dpg.font(r"assets\fonts\NotoSans-Regular.ttf", 18) as main_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.add_font_range(0x2190, 0x219e)
        dpg.add_font_range(0x2100, 0x214f)
        dpg.add_font_range(0x2010, 0x2015)
    app_info.load_font(r"assets\fonts\NotoSans-Bold.ttf", 24, tag="title")
    app_info.load_font(r"assets\fonts\OpenSans-Bold.ttf", 18)
    app_info.load_font(r"assets\fonts\OpenSans-Regular.ttf", 18)
    app_info.load_font(r"assets\fonts\TisaSansPro-Regular.ttf", 18)
    app_info.load_font(r"assets\fonts\Roboto-Regular.ttf", 18)
    app_info.load_font(r"assets\fonts\Roboto-Medium.ttf", 18)
    app_info.load_font(r"assets\fonts\TisaSansPro-Regular.ttf", 18)
    app_info.load_font(r"assets\fonts\SourceSansPro-Regular.ttf", 18, tag="chain_of_plugins_font")

with dpg.texture_registry(tag="texture_registry"):
    dpg.add_raw_texture(2000, 2000, storage.current_data, format=dpg.mvFormat_Float_rgba, tag="main_image")
    app_info.add_static_texture(r"assets/images/go-to-begin-color.png", "go_to_begin_img")
    app_info.add_static_texture(r"assets/images/prev-frame-color.png", "prev_frame_img")
    app_info.add_static_texture(r"assets/images/play-color.png", "play_img")
    app_info.add_static_texture(r"assets/images/pause-color.png", "pause_img")
    app_info.add_static_texture(r"assets/images/next-frame-color.png", "next_frame_img")
    app_info.add_static_texture(r"assets/images/go-to-end-color.png", "go_to_end_img")
    app_info.add_static_texture(r"assets/images/help-24.png", "help_img")
    app_info.add_static_texture(r"assets/images/plus-24.png", "plus_img")
    app_info.add_static_texture(r"assets/images/minus-24.png", "minus_img")
    app_info.add_static_texture(r"assets/images/crosshair-three.png", "crosshair_img")

with dpg.handler_registry():
    dpg.add_mouse_release_handler(callback=pm.undragging)
    dpg.add_key_press_handler(78, callback=lambda: dpg.show_item("settings_of_the_program"))
    dpg.add_key_press_handler(65, callback=pm.apply_chain)
    dpg.add_key_press_handler(80, callback=lambda: dpg.show_item("plugins_window"))

with dpg.item_handler_registry(tag="image_handler_registry"):
    dpg.add_item_hover_handler(callback=pm.get_mouse_pos)
    dpg.add_item_clicked_handler(callback=pm.set_2d_point_values)

dpg.add_item_handler_registry(tag="none_handler")

with dpg.window(label="Управление обработкой изображений и видео", show=False, autosize=True, pos=(300, 100), 
tag="plugins_window", no_resize=True):
    #dpg.add_text("Пакеты плагинов:")
    #dpg.add_listbox(("(Вне пакетов)",), default_value="(Вне пакетов)", tag="packages_of_plugins", 
    #num_items=4)
    with dpg.group(horizontal=True, horizontal_spacing=12):
        with dpg.group():
            dpg.add_text("Плагины:")
            dpg.add_listbox(storage.plugins_titles, default_value=storage.plugins_titles[0], tag="list_of_plugins", 
            num_items=10, width=315, callback=pm.check_plugin, drag_callback=pm.drag_plugin, tracked=True)
            with dpg.drag_payload(parent="list_of_plugins", drag_data=0, payload_type="plugin", tag="drop_plugin"):
                dpg.add_text(dpg.get_value("list_of_plugins"), tag="drag_text")
            #dpg.bind_item_theme(dpg.last_container(), themes.get_popup_theme())
            with dpg.group(horizontal=True, tag="previous_warning_plugin", horizontal_spacing=3, show=False):
                dpg.add_text("Для работы требуются другие плагины", indent=12)
                dpg.add_image("help_img")
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Для использования данного плагина следует включить в цепочку перед ним "
                    "другие плагины или их дубликаты:", 
            tag="previous_warning_text", wrap=400)
                    dpg.add_text("В списке плагинов все предшествующие плагины присуствуют", color=(70, 204, 40),
                    tag="previous_plugins_state")
                    dpg.add_group(tag="previous_warning_tooltip")
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=33)
                dpg.add_button(label="Информация", callback=pm.more_plugin_info, tag="more_info_button", width=115)
                dpg.add_button(label="Настройки", callback=pm.open_plugin_settings, tag="open_settings_button", width=105)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=33)
                dpg.add_button(label="Дублировать", callback=pm.duplicate_plugin, width=120)
                dpg.add_button(label="Удалить", callback=None, enabled=False, width=100, tag="delete_from_plugins_list_button")
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=33)
                dpg.add_button(label="Добавить в цепочку плагинов", callback=pm.add_to_chain, tag="add_to_chain_of_plugins")
        with dpg.group():
            dpg.add_text("Цепочка плагинов:")
            dpg.add_listbox([], tag="plugins_in_chain", num_items=10, width=315, payload_type="plugin",
            drop_callback=lambda s, d: pm.add_to_chain(title=d), callback=pm.set_plugin_in_list)
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=30)
                    dpg.add_button(label="Вверх", callback=lambda: pm.swap("up"), enabled=False, tag="swap_up_button")
                    dpg.add_button(label="Вниз", callback=lambda: pm.swap("down"), enabled=False, tag="swap_down_button")
                    dpg.add_button(label="Удалить", callback=pm.delete_from_chain, enabled=False, 
                    tag="delete_from_chain_of_plugins_button")
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=30)
                    dpg.add_button(label="Загрузить", width=115, callback=lambda: dpg.show_item("json_open_dialog"))
                    dpg.add_button(label="Применить", width=115, callback=pm.apply_chain)
                dpg.add_text("В демо-версии можно добавить не более 5 \nплагинов в цепочку", color=(230, 0, 0), 
                show=False, tag="limit_5_plugins")

with dpg.window(label="Добавить URL", show=False, width=600, height=400, tag="add_urls_window"):
    dpg.add_text("Добавьте URL (с новой строки):")
    dpg.add_input_text(multiline=True, tag="urls")
    dpg.add_button(label="Добавить URL", callback=fo.open_objects, user_data=OBJECT_TYPES.url)

# диалоговое окно открытия файлов
with dpg.file_dialog(label="Открыть объекты", callback=fo.open_objects, directory_selector=False,
show=False, tag="pc_file_dialog", user_data=OBJECT_TYPES.file, default_path="E:/opencv", width=800, height=600):
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
with dpg.file_dialog(label="Сохранить все объекты", callback=fo.save_all_files, directory_selector=True,
show=False, tag="save_files_dialog", width=800, height=600):
    dpg.add_checkbox(label="Показать отчёт", default_value=True, tag="show_report")
    dpg.add_text("Сохранить под именами:")
    dpg.add_radio_button(items=("Исходные имена", "Программное имя"), tag="set_program_name",
    default_value="Исходные имена", callback=app_info.set_group_program_name_visible)
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

# диалоговое окно открытия файлов (для настроек плагинов)
with dpg.file_dialog(label="Открыть объекты", callback=pm.file_set_path, directory_selector=False, show=False, 
tag="pc_file_plugin_dialog", default_path="D:", file_count=1, width=800, height=600):
    dpg.add_file_extension(".*")

# диалоговое окно открытия JSON-файлов
with dpg.file_dialog(label="Открыть цепочку плагинов из файла", callback=pm.open_chain_from_file, 
directory_selector=False, show=False, default_path="E:/opencv", file_count=1, width=800, height=600, tag="json_open_dialog"):
    dpg.add_file_extension(".json", color=(255, 150, 150, 255), custom_text="[Configuration]")

with dpg.window(tag="objects_window"):
    with dpg.viewport_menu_bar(tag="main_menu"):
        with dpg.menu(label="Файл"):
            with dpg.menu(label="Открыть"):
                dpg.add_menu_item(label="Файлы с компьютера", callback=lambda: dpg.show_item("pc_file_dialog"))
                dpg.add_menu_item(label="Папку", callback=lambda: dpg.show_item("pc_folder_dialog"))
                dpg.add_menu_item(label="Изображения из интернета", callback=lambda: dpg.show_item("add_urls_window"),
                tag="upload_images_from_internet")
            with dpg.menu(label="Сохранить"):
                dpg.add_menu_item(label="Сохранить изображение", callback=None, tag="save_one_image_menu_item", 
                enabled=False) # TODO
                dpg.add_menu_item(label="Сохранить все изображения", callback=lambda: dpg.show_item("save_files_dialog")
                , tag="save_all_images_menu_item", enabled=False)
                dpg.add_menu_item(label="Сохранить кадр из видео", callback=None, tag="save_one_frame_menu_item",
                enabled=False) # TODO
                dpg.add_menu_item(label="Сохранить все кадры из видео", callback=None, tag="save_all_frames_menu_item",
                enabled=False) # TODO
            with dpg.menu(label="Закрыть"):
                dpg.add_menu_item(label="Закрыть объект", callback=fo.close_object, tag="close_object_menu_item", 
                enabled=False)
                dpg.add_menu_item(label="Закрыть все", callback=fo.close_all_objects, tag="close_all_objects_menu_item", 
                enabled=False)
        dpg.add_menu_item(label="Плагины", callback=lambda: dpg.show_item("plugins_window"))
        with dpg.menu(label="Лицензия"):
            dpg.add_menu_item(label="Просмотреть файл ключа", callback=usbkey.view_key)
            dpg.add_menu_item(label="Параметры ключа", callback=usbkey.key_params)
            dpg.add_menu_item(label="Проверить файл ключа", callback=usbkey.check_key_with_window)
        with dpg.menu(label="Приложение"):
            dpg.add_menu_item(label="Настройки", callback=lambda: dpg.show_item("settings_of_the_program"), shortcut="N")
            dpg.add_menu_item(label="Демо-версия", tag="demo_menu_item",
            callback=lambda: dpg.show_item("demo_version_description"), show=False)
            dpg.add_menu_item(label="Горячие клавиши", callback=lambda: dpg.show_item("hotkeys_window"))
            dpg.add_menu_item(label="О программе", callback=lambda: dpg.show_item("info_about_the_program"))
            #dpg.add_menu_item(label="Закрыть приложение", callback=app_info.save_init)
    dpg.bind_font(main_font)

    with dpg.group(show=False, tag="group_of_objects"):
        dpg.add_spacer(height=25)
        dpg.add_text("Перейти к объекту: ")
        dpg.add_combo(items=(), tag="combo_of_objects", callback=fo.change_object, width=500)

        dpg.add_spacer(height=10)
        dpg.add_text("Цепочка плагинов:")
        with dpg.group(horizontal=True):
            dpg.add_text("Нет плагинов", tag="chain_of_plugins")
            with dpg.group():
                dpg.add_spacer()
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Редактировать", callback=lambda: dpg.show_item("plugins_window"))
                    dpg.add_button(label="Применить", callback=pm.apply_chain, 
                    show=not storage.program_settings["auto_apply"], tag="apply_chain_of_plugins_button")
                    #dpg.add_button(label="Применить ко всем кадрам", callback=pm.apply_chain, 
                    #show=not storage.program_settings["auto_apply"], tag="apply_chain_of_plugins_button")
                    dpg.bind_item_font("chain_of_plugins", "chain_of_plugins_font")
        dpg.add_spacer(height=5)

        with dpg.group(tag="limit_1_minute"):
            dpg.add_text("""В демо-версии можно загружать ролики не длиннее 1 минуты!
    Для получения всех функций активируйте приложение.""", color=(230, 0, 0))
            dpg.add_spacer(height=10)

        with dpg.group(show=True, tag="state_of_loading"):
            with dpg.group(horizontal=True):
                #dpg.add_loading_indicator(circle_count=6, speed=2, style=0, radius=1.5)
                dpg.add_text("Загрузка плагина...", tag="text_of_loading")
                dpg.add_progress_bar(tag="progress_bar", width=300, show=False)
                dpg.add_spacer(height=10)

        with dpg.collapsing_header(label="Результаты обработки изображения при помощи плагинов", show=False, tag="additional_text", closable=True):
            dpg.add_spacer()
            with dpg.group(horizontal=True, indent=15):
                dpg.add_button(label="Копировать всё", callback=app_info.copy_all_additional_data)
                dpg.add_button(label="Развернуть все блоки", callback=lambda: app_info.manage_all_headers("expand"))
                dpg.add_button(label="Свернуть все блоки", callback=lambda: app_info.manage_all_headers("roll up"))
            dpg.add_spacer()
            dpg.add_group(tag="additional_text_group", indent=18)

            dpg.add_spacer(height=10)
        with dpg.collapsing_header(label="Результаты обработки видео при помощи плагинов", show=False, tag="video_data", closable=True):
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_spacer(height=3)
                    dpg.add_text("В отдельном окне: ")
                with dpg.child_window(horizontal_scrollbar=True, height=44):
                    dpg.add_group(horizontal=True, tag="plot_buttons")
            with dpg.child_window(horizontal_scrollbar=True, height=278):
                dpg.add_group(horizontal=True, tag="video_data_group")

        # видеопроигрыватель
        with dpg.group(tag="video_player", show=False):
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label="Применять плагины ко всем кадрам", default_value=True, tag="apply_to_all_frames")
                dpg.add_image("help_img")
                with dpg.tooltip(dpg.last_item()):
                    with dpg.group(horizontal=True):
                        dpg.add_spacer()
                        dpg.add_text("Включение данной настройки позволит не тратить время на применение плагинов к каждому отдельному " +
                        "кадру при переключении кадров. При изменении текущих примененных плагинов обрабатываются все изображения разом.", wrap=600)
                        dpg.add_spacer()
                    dpg.add_spacer()
            #dpg.add_spacer(height=3)

            with dpg.group(horizontal=True, tag="video_buttons"):
                dpg.add_image_button("go_to_begin_img", callback=pv.go_to_begin)
                dpg.add_image_button("prev_frame_img", callback=pv.go_to_prev_frame)
                dpg.add_image_button("next_frame_img", callback=pv.go_to_next_frame)
                dpg.add_image_button("go_to_end_img", callback=pv.go_to_end)
                with dpg.group():
                    dpg.add_spacer(height=0)
                    dpg.add_text("0 кадров/сек", color=(0, 206, 0), tag="speed_frames_text", show=False)
            with dpg.group(horizontal=True, tag="video_slider_group"):
                dpg.add_image_button("play_img", tag="play_button", callback=pv.toggle_play)
                dpg.bind_item_theme(dpg.last_item(), themes.get_button_theme())
                with dpg.group():
                    dpg.add_spacer(height=0)
                    with dpg.group(horizontal=True):
                        dpg.add_slider_int(width=400, format="%d/0", tag="video_slider", clamped=True, 
                        callback=lambda sender, app_data: pv.open_frame(app_data))
                        dpg.add_text("00:00", tag="video_time")
                        dpg.add_image("help_img")
                        with dpg.tooltip(dpg.last_item()):
                            dpg.add_text("Ctrl+Click на слайдере — ввод кадра")
                dpg.add_spacer(width=438, tag="third_spacer", show=False)
                with dpg.group():
                    dpg.add_spacer(height=0)
                    with dpg.group(horizontal=True):
                        dpg.add_image_button("plus_img", callback=lambda: pv.zoom("plus"), tag="plus_zoom_button")
                        dpg.bind_item_theme(dpg.last_item(), themes.get_button_theme())
                        dpg.add_image_button("minus_img", callback=lambda: pv.zoom("minus"), tag="minus_zoom_button")
                        dpg.bind_item_theme(dpg.last_item(), themes.get_button_theme())
                        dpg.add_button(label="100%", tag="100_zoom_button", show=False, callback=lambda: pv.zoom("100"))
                        dpg.bind_item_theme(dpg.last_item(), themes.get_button_theme())
                        dpg.add_text("100%", tag="zoom_text")
        dpg.add_spacer()
        with dpg.child_window(horizontal_scrollbar=True, tag="main_image_child_window", autosize_x=True, show=False):
            dpg.add_image("main_image", tag="main_image_desk")
        dpg.add_button(label="Закрыть и удалить временные файлы", tag="close_and_delete_temp_files", show=False,
        callback=pv.delete_temp_folders_and_close_video)

    with dpg.group(tag="hello_text", indent=5):
        dpg.add_spacer(height=25)
        dpg.add_text("Приветствуем вас в программе Computer Vision Experiments!")
        dpg.bind_item_font(dpg.last_item(), font="title")
        dpg.add_text("Открыть файлы:")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Из компьютера", callback=lambda: dpg.show_item("pc_file_dialog"))
            dpg.add_button(label="Из папки", callback=lambda: dpg.show_item("pc_folder_dialog"))
            dpg.add_button(label="Из интернета", tag="open_from_internet_button"
            , callback=lambda: dpg.show_item("add_urls_window"), enabled=False)

    with dpg.group(show=False, tag="report_of_processing"):
        dpg.add_spacer(height=10)
        dpg.add_text('Время обработки изображений: ', tag="time_of_processing")
        dpg.add_text('Обработано потоками изображений: ', tag="count_of_images_processing")
        dpg.add_button(label="Закрыть", callback=lambda: dpg.hide_item("report_of_processing"))
        #dpg.add_button(label="Показать график", callback=app_info.show_plot)

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
        dpg.add_button(label="Сохранить настройки", callback=app_info.save_program_settings)
        dpg.add_text("Настройки сохранены", show=False, tag="settings_of_program_have_saved")

with dpg.window(label="О программе", show=False, tag="info_about_the_program", no_resize=True, pos=(300, 100)):
    dpg.add_text("Программа Computer Vision Experiments")
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

dpg.bind_theme(themes.get_theme())
#dpg.bind_item_theme("objects_window", themes.get_theme())
dpg.bind_item_theme("video_buttons", themes.get_button_theme())
dpg.bind_item_theme("main_menu", themes.get_menu_theme())

dpg.show_style_editor()
#dpg.show_debug()
#dpg.show_metrics()
warnings.filterwarnings("ignore") # игнорирование предупреждений

#dpg.configure_app(init_file="C:/ProgramData/cv_experiments/dpg.ini")
dpg.create_viewport(title='Computer Vision Experiments', width=1200, height=700, x_pos=350, y_pos=150)

# must be called before showing viewport
dpg.set_viewport_small_icon("assets/images/icon.ico")
dpg.set_viewport_resize_callback(app_info.on_resize_viewport)

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
        if dpg.get_frame_count() % 20 == 0:
            dpg.set_value("speed_frames_text", f"{fps} кадров/сек")
            if fps >= storage.frame_rate:
                dpg.hide_item("speed_frames_text")
            if fps >= 24 and fps < storage.frame_rate:
                dpg.show_item("speed_frames_text")
                dpg.configure_item("speed_frames_text", color=(219, 179, 0))
            if fps < 24:
                dpg.show_item("speed_frames_text")
                dpg.configure_item("speed_frames_text", color=(249, 27, 42))
        # для соответствия воспроизведения частоты кадров видео и частоты обновления экрана
        time.sleep(max(0.0, 1/storage.frame_rate - dpg.get_delta_time()))
    dpg.render_dearpygui_frame()

dpg.destroy_context()

usbkey.write_in_journal(key_module.records.program_has_closed)