# -*- coding: utf-8 -*-
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 自動載入系統中的中文字體，並設定為 matplotlib 的預設字體
def setup_chinese_font():

    # 根據作業系統選擇字體路徑
    if sys.platform.startswith("linux"):
        font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    elif sys.platform.startswith("win"):
        font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    elif sys.platform.startswith("darwin"):
        font_path = "/System/Library/Fonts/STHeiti Light.ttc"
    else:
        raise EnvironmentError("不支援的作業系統")

    # 檢查字體檔是否存在
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"找不到中文字體檔：{font_path}，請安裝相應中文字體")

    # 設定 matplotlib 字體
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()
    print(f"✅ 已載入中文字體：{prop.get_name()}")

    # 回傳字體屬性物件
    return prop