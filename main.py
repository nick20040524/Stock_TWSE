# -*- coding: utf-8 -*-

# 自定函式套件
from twse_stock_info import twse_stock_info
from get_tw_stock_data import get_tw_stock_data
from update_stock_data_incrementally import update_stock_data_incrementally
from check_fallback_csvs import check_fallback_csvs

stock_info_df = twse_stock_info()
semi_df = stock_info_df.loc[(stock_info_df['上市有價證券種類']  == '股票') & (stock_info_df['產業別'] == '半導體業')]
stock_code_list = list(semi_df['有價證券代號代碼'])

# 上市日欄位轉換（若尚未處理）
semi_df.loc[:, "上市日"] = pd.to_datetime(semi_df["上市日"], errors="coerce")

# 指定欲更新的股票代碼（例：台積電、聯詠等）
stock_codes = ['2454', '2330']
stock_df = semi_df[semi_df['有價證券代號代碼'].isin(stock_codes)].copy()

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