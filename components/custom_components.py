import dearpygui.dearpygui as dpg
from components.functions import AppInfo as app_info
import components.styling as themes
from components.storage import OBJECT_STATUSES
import components.file_operations as fo

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
    if not disabled:
        open_file_menu_item_registry = app_info.buttonize_menu_item(tag, callback)
        dpg.bind_item_handler_registry(tag, open_file_menu_item_registry)

def enable_menu_item(tag, callback=None):
    open_file_menu_item_registry = app_info.buttonize_menu_item(tag, callback)
    dpg.bind_item_handler_registry(tag, open_file_menu_item_registry)
    dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[1], color=(51, 51, 51))
    dpg.set_item_user_data(tag, user_data={"disabled": False})

def disable_menu_item(tag):
    dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[1], color=(194, 194, 194))
    dpg.bind_item_handler_registry(tag, "none_handler")
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
            handler_registry = app_info.buttonize(f"file_{filename}", lambda: fo.change_object(filename))
            dpg.bind_item_handler_registry(f"file_{filename}", handler_registry)

def set_file_current(filename):
    file_group = dpg.get_item_children(f"file_{filename}", slot=1)[1]
    dpg.add_image("current_file", parent=file_group)

def delete_file_current(filename):
    file_group = dpg.get_item_children(f"file_{filename}", slot=1)[1]
    dpg.delete_item(dpg.get_item_children(file_group, slot=1)[2])