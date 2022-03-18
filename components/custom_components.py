import dearpygui.dearpygui as dpg
from components.functions import AppInfo as app_info
import components.styling as themes

def menu_item(label, parent, callback=None, shortcut=None, tag=None, 
spacer_width=0, disabled=False, demo=False, width=255):
    with dpg.child_window(height=32, width=width, tag=tag, parent=parent):
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

def disable_menu_item(tag):
    dpg.configure_item(dpg.get_item_children(dpg.get_item_children(tag, slot=1)[1], slot=1)[1], color=(194, 194, 194))
    dpg.bind_item_handler_registry(tag, "none_handler")