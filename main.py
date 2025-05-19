# -*- coding: utf-8 -*-
# 自訂函式引入
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
# 函式庫引入
import pandas as pd
from IPython.display import display

# 略過憑證驗證的警告，非錯誤，是urllib3 在提醒你：「你正在跳過 SSL 憑證驗證」
# 這些警告出現在 verify=False 時屬於預期行為，不影響程式執行
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=Warning, module="urllib3")

# 是否驗證 SSL 憑證（False 可避免 TWSE 出錯）
verify_ssl = False

# 設定中文字體以供 matplotlib 繪圖使用，避免亂碼
prop = setup_chinese_font()

# 取得 TWSE 股票清單
stock_info_df = twse_stock_info(use_cache=False, verify_ssl=False)

# 加入防呆判斷（避免 DataFrame 是空的或格式錯誤）
if stock_info_df.empty or "有價證券代號代碼" not in stock_info_df.columns:
    print("❌ TWSE 股票清單無法取得或格式錯誤，終止執行")
    exit()

# 指定要預測的股票代碼
stock_codes = get_target_codes()

# 篩選出目標股票詳細資訊並轉換上市日格式
stock_df = stock_info_df[stock_info_df["有價證券代號代碼"].isin(stock_codes)].copy()
stock_df["上市日"] = pd.to_datetime(stock_df["上市日"], errors="coerce")

# 檢查股票代碼是否在清單中（排除錯誤代碼）
found_codes = stock_df["有價證券代號代碼"].tolist()
missing_codes = [code for code in stock_codes if code not in found_codes]
if missing_codes:
    print("📛 以下股票代碼無法在 TWSE 清單中找到：", missing_codes)

# 更新每支股票資料歷史資料(增量更新)
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

# 檢查 fallback 資料是否有效（筆數、可讀性）
valid_codes, summary = check_fallback_csvs(stock_codes)
display(summary)
print("✅ 可用的股票代碼:", valid_codes)

# 對有效股票執行預測並收集結果
result_df = predict_multiple_stocks(valid_codes)
# 若有結果，執行圖表輸出與報表匯出
if not result_df.empty:
    # 將每支股票的圖表存為個別檔案
    plot_predictions(result_df, output_dir="charts", prop=prop)

    # 匯出 Excel 報表
    export_prediction_summary(result_df, "prediction_report.xlsx")
# 若沒有任何預測結果，提示無可用預測資料，可能原因：無效資料或模型未能訓練
else:
    print("⚠️ 沒有可用的預測結果")
