# -*- coding: utf-8 -*-
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def setup_chinese_font():
    if sys.platform.startswith("linux"):
        font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    elif sys.platform.startswith("win"):
        font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    elif sys.platform.startswith("darwin"):
        font_path = "/System/Library/Fonts/STHeiti Light.ttc"
    else:
        raise EnvironmentError("不支援的作業系統")

    if not os.path.exists(font_path):
        raise FileNotFoundError(f"找不到中文字體檔：{font_path}，請安裝相應中文字體")

    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
    print(f"✅ 已載入中文字體：{prop.get_name()}")
    return prop
