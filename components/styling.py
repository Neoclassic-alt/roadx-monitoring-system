import dearpygui.dearpygui as dpg

def get_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvAll, parent=theme, enabled_state=True):
        
        #dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (235, 235, 242), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (234, 234, 254), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (220, 220, 220), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (255, 255, 255, 0), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (127, 23, 211), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (255, 255, 255, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (51, 51, 51), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (210, 210, 210), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (246, 246, 246), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (29, 151, 236), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (56, 163, 236), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (154, 194, 242), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (154, 194, 242), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (192, 229, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (168, 168, 255), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_Button, (194, 194, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (237, 245, 252), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (221, 236, 249), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (235, 235, 242), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (92, 190, 234), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (194, 194, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (168, 168, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Header, (194, 194, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Tab, (118, 118, 200), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (154, 194, 242), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGrip, (154, 194, 242), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGripHovered, (194, 194, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGripActive, (168, 168, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_DragDropTarget, (63, 12, 204), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Separator, (228, 228, 228), category=dpg.mvThemeCat_Core)
        
        #dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 6, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 8, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 5, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5, 0.5, category=dpg.mvThemeCat_Core)

        dpg.add_theme_style(dpg.mvPlotStyleVar_LegendInnerPadding, 8, 6, category=dpg.mvThemeCat_Plots)
        
        dpg.add_theme_color(dpg.mvPlotCol_FrameBg, (154, 214, 233), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_PlotBg, (255, 255, 255), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_LegendBg, (235, 250, 255), category=dpg.mvThemeCat_Plots)
        
        #dpg.add_theme_color(dpg.mvPlotCol_)

    #with dpg.theme_component(parent=theme):
    #    dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)
    #    dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)
    #    dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, 0, category=dpg.mvThemeCat_Core)
    #    dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (255, 255, 255))
    #with dpg.theme_component(dpg.mvDragPayload, parent=theme):
    #    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_Pa, 0, 0, category=dpg.mvThemeCat_Core)
    #    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core)
    #    dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvChildWindow, parent=theme, enabled_state=True):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvButton, parent=theme, enabled_state=False):
        #dpg.add_theme_color(dpg.mvThemeCol_Button, (198, 198, 198), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (160, 160, 160), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (198, 198, 198), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (198, 198, 198), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (160, 160, 160), category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvMenuItem, parent=theme, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (70, 70, 70), category=dpg.mvThemeCat_Core)

    return theme

def null_padding_primary_window():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvWindowAppItem, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 6, category=dpg.mvThemeCat_Core)

    return theme

def get_button_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 16, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 2, 2, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 16, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvImageButton, parent=theme, enabled_state=False):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 2, 2, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 16, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_Button, (198, 198, 198), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (198, 198, 198), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (198, 198, 198), category=dpg.mvThemeCat_Core)
    return theme

def get_menu_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)
        dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, 0)
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (255, 255, 255))

    return theme

def get_line_fill_theme(color):
    theme = dpg.add_theme()
    with dpg.theme_component(parent=theme):
        dpg.add_theme_color(dpg.mvPlotCol_Line, color, category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_Fill, color, category=dpg.mvThemeCat_Plots)
    return theme

def get_crosshair_button_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 16, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (194, 194, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (155, 155, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (117, 117, 255), category=dpg.mvThemeCat_Core)
    return theme

def get_green_crosshair_button_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 16, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (95, 239, 141), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (96, 255, 146), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (86, 216, 127), category=dpg.mvThemeCat_Core)
    return theme

def default_button_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
    return theme

def hover_button_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (237, 245, 252), category=dpg.mvThemeCat_Core)
    return theme

def active_button_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (221, 236, 249), category=dpg.mvThemeCat_Core)
    return theme

def add_files_button_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 6, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (242, 251, 222), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (227, 242, 194), category=dpg.mvThemeCat_Core)
    return theme

def group_buttons_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8, category=dpg.mvThemeCat_Core)
    return theme

def blue_button_square_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (237, 245, 252), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (221, 236, 249), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvImageButton, parent=theme, enabled_state=False):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4, category=dpg.mvThemeCat_Core)
    return theme

def green_button_square_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (242, 251, 222), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (227, 242, 194), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvImageButton, parent=theme, enabled_state=False):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4, category=dpg.mvThemeCat_Core)
    return theme

def zoom_ind_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (237, 245, 252), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (221, 236, 249), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (64, 149, 227), category=dpg.mvThemeCat_Core)
    return theme

def close_button_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (252, 237, 237), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 205, 205), category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvImageButton, parent=theme, enabled_state=False):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255), category=dpg.mvThemeCat_Core)
    return theme

def white_background():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
    return theme

def window_shadow():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvWindowAppItem, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 10), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 1, 1, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 30), category=dpg.mvThemeCat_Core)
    return theme

def splash_window():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (250, 250, 250), category=dpg.mvThemeCat_Core)
    return theme

def default_menu_item_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
    return theme

def hover_menu_item_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (237, 245, 252), category=dpg.mvThemeCat_Core)
    return theme

def active_menu_item_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (221, 236, 249), category=dpg.mvThemeCat_Core)
    return theme

def player_pan(opacity):
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255, opacity), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4, category=dpg.mvThemeCat_Core)
    return theme

def player_window(opacity):
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvWindowAppItem, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, opacity // 6.3), category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0, opacity), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 20, opacity), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 40, opacity), category=dpg.mvThemeCat_Core)
    return theme

def lock_button(opacity):
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvImageButton, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0, opacity), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 20, opacity), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 40, opacity), category=dpg.mvThemeCat_Core)
    return theme

def player_progress(opacity):
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (64, 149, 227, opacity), category=dpg.mvThemeCat_Core)
    return theme

def delete_button():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvButton, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (249, 80, 80), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (249, 80, 80), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 205, 205), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4, category=dpg.mvThemeCat_Core)
    return theme

def cancel_button():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvButton, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (252, 237, 237), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 205, 205), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (253, 62, 62), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4, category=dpg.mvThemeCat_Core)
    return theme

def window_theme():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvWindowAppItem, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 10, category=dpg.mvThemeCat_Core)
    return theme

def search_field():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (246, 246, 246), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 4, category=dpg.mvThemeCat_Core)
    return theme

def close_all_objects_button_default():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (253, 62, 62), category=dpg.mvThemeCat_Core)
    return theme

def close_all_objects_button_hover():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (252, 237, 237), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (253, 62, 62), category=dpg.mvThemeCat_Core)
    return theme

def thin_scrollbar():
    theme = dpg.add_theme()
    with dpg.theme_component(dpg.mvChildWindow, parent=theme):
        dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 10, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
    return theme