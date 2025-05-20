# -*- coding: utf-8 -*-
from stock.twse_stock_info import twse_stock_info 
from stock.update_module import (
    get_target_codes,
    update_stock_data_incrementally,
    check_fallback_csvs
)
from stock.predict_and_export import (
    predict_multiple_stocks,
    plot_predictions,
    export_prediction_summary
)
from stock.setup_chinese_font import setup_chinese_font
import pandas as pd
import os
import warnings
from IPython.display import display

# 🔐 忽略 SSL 驗證警告
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning, module="urllib3")

# 🔧 是否驗證 SSL 憑證（False 可避免 TWSE 出錯）
verify_ssl = False

# 📁 顯示目前執行目錄
print("📂 當前工作目錄：", os.getcwd())

# 🈶 設定中文字體
prop = setup_chinese_font()

# 📥 擷取 TWSE 股票清單
stock_info_df = twse_stock_info(use_cache=False, verify_ssl=verify_ssl)

# 🧱 防呆：檢查欄位存在與資料是否有效
if stock_info_df.empty or "有價證券代號代碼" not in stock_info_df.columns:
    print("❌ TWSE 股票清單無法取得或格式錯誤，終止執行")
    exit()

# 🎯 指定目標股票清單
stock_codes = get_target_codes()

# 🔍 篩選出在清單內的合法股票，轉換上市日格式
stock_df = stock_info_df[stock_info_df["有價證券代號代碼"].isin(stock_codes)].copy()
stock_df["上市日"] = pd.to_datetime(stock_df["上市日"], errors="coerce")

# ❗ 檢查是否有輸入錯誤的代碼
found_codes = stock_df["有價證券代號代碼"].tolist()
missing_codes = [code for code in stock_codes if code not in found_codes]
if missing_codes:
    print("📛 以下股票代碼無法在 TWSE 清單中找到：", missing_codes)

# 🔄 更新每支股票資料（歷史增量更新）
for _, row in stock_df.iterrows():
    try:
        update_stock_data_incrementally(
            stock_code=row["有價證券代號代碼"],
            stock_name=row["有價證券代號名稱"],
            listed_date=row["上市日"],
            verify_ssl=verify_ssl
        )
    except Exception as e:
        print(f"❌ 更新 {row['有價證券代號代碼']} 發生錯誤：{e}")

# ✅ 檢查 fallback 資料是否可用
valid_codes, summary = check_fallback_csvs(stock_codes)
display(summary)
print("✅ 可用的股票代碼:", valid_codes)

# 🧠 使用模型進行預測（自動訓練或載入）
result_df = predict_multiple_stocks(valid_codes)

# 📈 若有結果，進行圖表與報表輸出
if not result_df.empty:
    plot_predictions(result_df, output_dir="charts", prop=prop)
    export_prediction_summary(result_df, "prediction_report.xlsx")
else:
    print("⚠️ 沒有可用的預測結果（可能是 fallback 無資料或模型訓練失敗）")
