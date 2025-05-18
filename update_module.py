import os
import pandas as pd
from datetime import datetime, timedelta, date
import time
import random
import requests as r
from lxml import etree

# --- 單支股票抓資料 ---
def get_tw_stock_data(start, end, stock_code, listed_date):
    session = r.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    month_list = pd.date_range(start, end, freq='MS')
    dfs = []

    for month in month_list:
        if month < listed_date:
            continue
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={month.strftime('%Y%m%d')}&stockNo={stock_code}"

        try:
            res = session.get(url, headers=headers, timeout=10)
            js = res.json()
            if js.get("stat") != "OK":
                continue
            df_m = pd.DataFrame(js.get("data", []), columns=js.get("fields", []))
            df_m["日期"] = df_m["日期"].str.split("/").apply(lambda x: datetime(int(x[0]) + 1911, int(x[1]), int(x[2])))
            for col in ["成交股數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差", "成交筆數"]:
                df_m[col] = pd.to_numeric(df_m[col].str.replace("[,X]", "", regex=True), errors='coerce')
            df_m.insert(0, "股票代碼", stock_code)
            dfs.append(df_m)
            time.sleep(random.uniform(0.5, 1.0))
        except Exception as e:
            print(f"錯誤：{stock_code} {month.strftime('%Y-%m')} => {e}")
            continue

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


# --- 資料更新 ---
def update_stock_data_incrementally(stock_code, stock_name, listed_date, fallback_dir="."):
    if pd.isna(listed_date):
        print(f"⚠️ {stock_code} 上市日無法解析，📛 目前不支援此標的")
        return

    fallback_path = os.path.join(fallback_dir, f"fallback_{stock_code}.csv")
    if os.path.exists(fallback_path):
        df_old = pd.read_csv(fallback_path, encoding="utf-8-sig", parse_dates=["日期"])
        last_date = df_old["日期"].max().date()
        print(f"📄 發現 {stock_code} 現有資料，最後日期為 {last_date}")
        start = last_date + timedelta(days=1)
    else:
        df_old = pd.DataFrame()
        start = listed_date.date()
        print(f"🆕 初次建立 {stock_code} 資料檔，從 {start} 開始抓取")

    today = date.today()
    if start > today:
        print(f"✅ {stock_code} 已為最新，無需更新")
        return

    df_new = get_tw_stock_data(start, today, stock_code, listed_date)
    if df_new.empty:
        print(f"⚠️ {stock_code} 沒有抓到新資料")
        return

    df_new.insert(1, "有價證券代號名稱", stock_name)
    df_final = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=["日期"])
    df_final = df_final.sort_values(by="日期")
    df_final.to_csv(fallback_path, index=False, encoding="utf-8-sig")
    print(f"✅ {stock_code} 資料更新完成，共 {len(df_final)} 筆")


# --- fallback CSV 檢查 ---
def check_fallback_csvs(stock_codes, fallback_dir="."):
    results = []
    for code in stock_codes:
        path = os.path.join(fallback_dir, f"fallback_{code}.csv")
        if not os.path.exists(path):
            print(f"📛 無法找到 fallback_{code}.csv，⚠️ 目前不支援此標的")
            results.append({"股票代號": code, "狀態": "❌ 檔案不存在", "筆數": 0})
            continue
        try:
            df = pd.read_csv(path, parse_dates=["日期"])
            count = len(df.dropna(subset=["收盤價", "成交股數"]))
            if count < 10:
                results.append({"股票代號": code, "狀態": f"⚠️ 資料過少（{count} 筆）", "筆數": count})
            else:
                results.append({"股票代號": code, "狀態": "✅ 有效", "筆數": count})
        except Exception as e:
            results.append({"股票代號": code, "狀態": f"❌ 讀取錯誤: {e}", "筆數": 0})
    df = pd.DataFrame(results)
    valid_codes = df[df["狀態"] == "✅ 有效"]["股票代號"].tolist()
    return valid_codes, df


# --- 從股票清單挑選欲處理的股票 ---
def prepare_stock_update(stock_info_df, stock_codes):
    stock_df = stock_info_df[stock_info_df["有價證券代號代碼"].isin(stock_codes)].copy()
    stock_df["上市日"] = pd.to_datetime(stock_df["上市日"], errors="coerce")
    found_codes = stock_df["有價證券代號代碼"].tolist()
    missing_codes = [code for code in stock_codes if code not in found_codes]
    if missing_codes:
        print("📛 以下代碼無法在 TWSE 股票清單中找到（可能為下市、興櫃或代號錯誤）：", missing_codes)
    return stock_df

# --- 指定目標股票標的代碼 ---
def get_target_codes():
    # 這裡可以根據需求修改，或從其他來源讀取
    return ['2330', '2454', '1590', '6669']

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