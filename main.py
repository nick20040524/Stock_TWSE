# 設定中文字體
prop = setup_chinese_font()

# 取得股票清單
stock_info_df = twse_stock_info()

# 指定要預測的股票代碼
stock_codes = get_target_codes()

# 擷取對應股票資料
stock_df = stock_info_df[stock_info_df["有價證券代號代碼"].isin(stock_codes)].copy()
stock_df["上市日"] = pd.to_datetime(stock_df["上市日"], errors="coerce")

# 檢查無效代碼
found_codes = stock_df["有價證券代號代碼"].tolist()
missing_codes = [code for code in stock_codes if code not in found_codes]
if missing_codes:
    print("📛 以下股票代碼無法在 TWSE 清單中找到：", missing_codes)

# 更新每支股票資料
for _, row in stock_df.iterrows():
    try:
        update_stock_data_incrementally(
            stock_code=row["有價證券代號代碼"],
            stock_name=row["有價證券代號名稱"],
            listed_date=row["上市日"]
        )
    except Exception as e:
        print(f"❌ 更新 {row['有價證券代號代碼']} 發生錯誤：{e}")

# 檢查 fallback 資料是否有效
valid_codes, summary = check_fallback_csvs(stock_codes)
display(summary)
print("✅ 可用的股票代碼:", valid_codes)

# 執行預測與報表輸出
result_df = predict_multiple_stocks(valid_codes)
if not result_df.empty:
    # 將每支股票的圖表存為個別檔案
    plot_predictions(result_df, output_dir="charts", prop=prop)

    # 匯出 Excel 報表
    export_prediction_summary(result_df, "prediction_report.xlsx")
else:
    print("⚠️ 沒有可用的預測結果")
