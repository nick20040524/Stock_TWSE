# -*- coding: utf-8 -*-
# 下載資料套件
import requests as r

# 資料處理套件
from lxml import etree
import json
from datetime import datetime, date
import pandas as pd
from datetime import datetime, date, timedelta
import time
import random

# 財經套件
import yfinance as yf

# 畫圖套件
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import subprocess
import os
from IPython.display import display

# 模型訓練函式
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# 自定義函式
from twse_stock_info import twse_stock_info
from update_module import twse_stock_info, get_tw_stock_data, update_stock_data_incrementally, check_fallback_csvs, get_target_codes, prepare_stock_update
from setup_chinese_font import setup_chinese_font

# 設定中文字體
prop = setup_chinese_font()

# 取得 TWSE 股票清單
stock_info_df = twse_stock_info()
semi_df = stock_info_df.loc[(stock_info_df['上市有價證券種類']  == '股票') & (stock_info_df['產業別'] == '半導體業')]
stock_code_list = list(semi_df['有價證券代號代碼'])

# 指定欲更新的股票代碼
stock_codes = get_target_codes()

# 從完整清單抓，不限半導體
stock_df = stock_info_df[stock_info_df['有價證券代號代碼'].isin(stock_codes)].copy()

# 上市日處理
stock_df.loc[:, "上市日"] = pd.to_datetime(stock_df["上市日"], errors="coerce")

# 顯示錯誤代碼
found_codes = stock_df['有價證券代號代碼'].tolist()
missing_codes = [code for code in stock_codes if code not in found_codes]
if missing_codes:
    print("📛 以下股票代碼無法在 TWSE 資料中找到（可能已下市或輸入錯誤）：", missing_codes)

# 一支一支更新資料，並儲存 fallback_xxx.csv
for _, row in stock_df.iterrows():
    try:
        update_stock_data_incrementally(
            stock_code=row["有價證券代號代碼"],
            stock_name=row["有價證券代號名稱"],
            listed_date=row["上市日"]
        )
    except Exception as e:
        print(f"❌ 更新 {row['有價證券代號代碼']} 發生錯誤：{e}")

# 執行檢查
valid_codes, summary = check_fallback_csvs(stock_codes, fallback_dir=".")

# 顯示檢查報告
from IPython.display import display
display(summary)

# 顯示哪些股票可以進入預測流程
print("✅ 可用的股票代號:", valid_codes)

# 一支一支更新資料，並儲存 fallback_xxx.csv
for _, row in stock_df.iterrows():
    try:
        update_stock_data_incrementally(
            stock_code=row["有價證券代號代碼"],
            stock_name=row["有價證券代號名稱"],
            listed_date=row["上市日"]
        )
    except Exception as e:
        print(f"❌ 更新 {row['有價證券代號代碼']} 發生錯誤：{e}")

# 執行檢查
valid_codes, summary = check_fallback_csvs(stock_codes, fallback_dir=".")

# 顯示檢查報告
from IPython.display import display
display(summary)

# 顯示哪些股票可以進入預測流程
print("✅ 可用的股票代號:", valid_codes)