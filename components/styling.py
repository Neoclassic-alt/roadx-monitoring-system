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
        dpg.add_theme_color(dpg.mvThemeCol_Border, (92, 190, 234), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_Border, (127, 23, 211), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (127, 23, 211), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (255, 255, 255, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (54, 54, 112), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (210, 210, 210), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
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
        #dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (155, 155, 255), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (117, 117, 255), category=dpg.mvThemeCat_Core)
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
        dpg.add_theme_color(dpg.mvThemeCol_Separator, (197, 197, 197), category=dpg.mvThemeCat_Core)
        
        #dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 6, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 15, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 8, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 8, 8, category=dpg.mvThemeCat_Core)
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