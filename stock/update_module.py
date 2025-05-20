# -*- coding: utf-8 -*-
import requests as r
import pandas as pd
from datetime import datetime, date, timedelta
import time
import random
import os
import certifi  # 為 SSL 驗證開關而加

# 抓取指定股票在指定時間範圍內的歷史交易資料，並轉換為 pandas DataFrame 格式
def get_tw_stock_data(start, end, stock_code, listed_date, verify_ssl=True):
    session = r.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    month_list = pd.date_range(start, end, freq='MS')
    dfs = []

    verify_mode = certifi.where() if verify_ssl else False

    for month in month_list:
        if month < listed_date:
            continue

        url = (
            f"https://www.twse.com.tw/exchangeReport/STOCK_DAY"
            f"?response=json&date={month.strftime('%Y%m%d')}&stockNo={stock_code}"
        )

        try:
            res = session.get(url, headers=headers, timeout=10, verify=verify_mode)
            js = res.json()
            if js.get("stat") != "OK":
                continue

            df_m = pd.DataFrame(js.get("data", []), columns=js.get("fields", []))
            df_m["日期"] = df_m["日期"].str.split("/").apply(
                lambda x: datetime(int(x[0]) + 1911, int(x[1]), int(x[2]))
            )

            for col in ["成交股數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差", "成交筆數"]:
                df_m[col] = pd.to_numeric(
                    df_m[col].str.replace("[,X]", "", regex=True), errors='coerce'
                )

            df_m.insert(0, "股票代碼", stock_code)
            dfs.append(df_m)
            time.sleep(random.uniform(0.5, 1.0))

        except Exception as e:
            print(f"❌ 錯誤：{stock_code} {month.strftime('%Y-%m')} => {e}")
            continue

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


# 自動更新 fallback 檔案（只補抓尚未有的區間）
def update_stock_data_incrementally(stock_code, stock_name, listed_date, fallback_dir=".", verify_ssl=True):
    if pd.isna(listed_date):
        print(f"⚠️ {stock_code} 上市日格式錯誤，無法處理")
        return

    fallback_path = os.path.join(fallback_dir, f"fallback_{stock_code}.csv")

    if os.path.exists(fallback_path):
        df_old = pd.read_csv(fallback_path, encoding="utf-8-sig", parse_dates=["日期"])
        last_date = df_old["日期"].max().date()
        print(f"📄 {stock_code} 已有資料，最後日期：{last_date}")
        start = last_date + timedelta(days=1)
    else:
        df_old = pd.DataFrame()
        start = listed_date.date()
        print(f"🆕 建立 {stock_code} 新資料檔，從 {start} 開始")

    today = date.today()
    if start > today:
        print(f"✅ {stock_code} 資料已為最新，略過更新")
        return

    df_new = get_tw_stock_data(start, today, stock_code, listed_date, verify_ssl=verify_ssl)
    if df_new.empty:
        print(f"⚠️ {stock_code} 沒有抓到新資料")
        return

    df_new.insert(1, "有價證券代號名稱", stock_name)
    df_final = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=["日期"])
    df_final = df_final.sort_values(by="日期")
    df_final.to_csv(fallback_path, index=False, encoding="utf-8-sig")
    print(f"✅ {stock_code} 更新完成，共 {len(df_final)} 筆")


# 檢查 fallback CSV 狀態（是否存在、格式正確？）
def check_fallback_csvs(stock_codes, fallback_dir="."):
    results = []

    for code in stock_codes:
        path = os.path.join(fallback_dir, f"fallback_{code}.csv")
        if not os.path.exists(path):
            print(f"📛 缺少 fallback_{code}.csv")
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

    df_result = pd.DataFrame(results)
    valid_codes = df_result[df_result["狀態"] == "✅ 有效"]["股票代號"].tolist()

    return valid_codes, df_result


# 預設要處理的股票代碼清單
def get_target_codes():
    return ['2330', '2454', '1590', '6669']