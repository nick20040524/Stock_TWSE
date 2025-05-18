from update_module import twse_stock_info, prepare_stock_update, update_stock_data_incrementally, check_fallback_csvs, get_target_codes

# 股票清單
target_codes = get_target_codes()

# 載入完整清單
stock_info_df = twse_stock_info()

# 準備更新清單
stock_df = prepare_stock_update(stock_info_df, target_codes)

# 執行更新
for _, row in stock_df.iterrows():
    update_stock_data_incrementally(
        stock_code=row["有價證券代號代碼"],
        stock_name=row["有價證券代號名稱"],
        listed_date=row["上市日"]
    )

# 檢查 fallback 檔
valid_codes, summary_df = check_fallback_csvs(target_codes)
print("✅ 可用股票：", valid_codes)
