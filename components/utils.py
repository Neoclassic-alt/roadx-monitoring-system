import dearpygui.dearpygui as dpg
from components.storage import storage

def load_font(url, size, tag = None):
    if not tag is None:
        with dpg.font(url, size, tag=tag):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.add_font_range(0x2190, 0x219e)
            dpg.add_font_range(0x2100, 0x214f)
            dpg.add_font_range(0x2010, 0x2015)
            dpg.add_font_chars([0x00D7, 0x2009])
    else:
        with dpg.font(url, size):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

def add_static_texture(url, tag):
    width, height, channels, data = dpg.load_image(url)
    dpg.add_static_texture(width, height, data, tag=tag)

def plural(count, one_form, two_form, three_form):
    if (count % 10) == 1 and (count > 20 or count == 1):
        return one_form
    if (count % 10) >= 2 and (count % 10) <= 4 and (count > 20 or count < 10):
        return two_form
    if (count % 10) >= 5 or (count % 10) == 0 or (count >= 10 and count <= 20):
        return three_form

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

def convert_to_index():
    return round(dpg.get_mouse_pos()[0] / dpg.get_item_width("player_pan") * storage.total_frames)

def convert_to_text_range(range, frame_rate):
    time_begin = range[0] / frame_rate
    time_end = range[1] / frame_rate
    minutes_begin = time_begin // 60
    seconds_begin = time_begin % 60
    minutes_end = time_end // 60
    seconds_end = time_end % 60
    return f"{range[0]}–{range[1]}" + " ({0:02d}:{1:02d} – {2:02d}:{3:02d})" \
    .format(int(minutes_begin), int(seconds_begin), int(minutes_end), int(seconds_end))

def convert_to_ranges(video_indexes, threshold, frame_rate):
    ranges = []
    prev_value = video_indexes[0]

    for i, index in enumerate(video_indexes):
        if i == 0:
            ranges.append([prev_value, prev_value])
            continue
        else:
            if index - prev_value <= 5:
                ranges[-1][1] = index
            else:
                ranges.append([index, index])
            prev_value = index
    ranges = [range for range in ranges if range[1] - range[0] >= threshold]
    ranges = list(map(lambda a: convert_to_text_range(a, frame_rate), ranges))
    return ranges