# -*- coding: utf-8 -*-
import requests as r
from lxml import etree
import pandas as pd
import time
import os
import certifi

def twse_stock_info(cache_file="twse_stock.csv", use_cache=True, verify_ssl=True):
    """
    從 TWSE 擷取股票清單，具備快取、錯誤重試與 SSL 憑證可關閉選項

    Args:
        cache_file (str): 快取檔名
        use_cache (bool): 是否使用快取
        verify_ssl (bool): 是否驗證 SSL 憑證（預設 True，測試時可設 False）

    Returns:
        pd.DataFrame: 股票資訊 DataFrame，欄位含「有價證券代號代碼」
    """
    if use_cache and os.path.exists(cache_file):
        print(f"📦 使用快取資料：{cache_file}")
        return pd.read_csv(cache_file, dtype=str)

    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    headers = {"User-Agent": "Mozilla/5.0"}

    # 根據選項決定是否驗證憑證
    verify_mode = certifi.where() if verify_ssl else False

    for i in range(3):
        try:
            res = r.get(url, headers=headers, timeout=10, verify=verify_mode)
            break
        except Exception as e:
            print(f"TWSE 第 {i+1} 次嘗試失敗：{e}")
            time.sleep(2)
    else:
        print("❌ 無法連線至 TWSE，請確認網路或稍後再試")
        return pd.DataFrame()

    res.encoding = 'big5'
    root = etree.HTML(res.text)
    data = root.xpath('//tr')[1:]

    df = pd.DataFrame(columns=[
        "上市有價證券種類", "有價證券代號代碼", "有價證券代號名稱",
        "國際證券辨識號碼(ISIN Code)", "上市日", "市場別",
        "產業別", "CFICode", "備註"
    ])

    category = ''
    row_num = 0
    for row in data:
        row = list(map(lambda x: x.text, row.iter()))[1:]

        if len(row) == 3:
            category = row[1].strip()

        elif len(row) >= 7:
            try:
                stock_code, stock_name = row[0].split('\u3000')
            except ValueError:
                print(f"⚠️ 無法分割代號與名稱：{row[0]}")
                continue

            if not (stock_code.isdigit() and len(stock_code) == 4):
                continue
            note = row[6]
            if note and isinstance(note, str) and "下市" in note:
                continue

            data_row = [category, stock_code, stock_name, row[1], row[2], row[3], row[4], row[5], row[6]]
            df.loc[row_num] = data_row
            row_num += 1

        else:
            print(f"⚠️ 欄位不足的資料列：{row}")
            continue

    df.to_csv(cache_file, index=False, encoding='utf-8-sig')
    print(f"💾 已儲存快取資料至：{cache_file}")
    return df