# -*- coding: utf-8 -*-
import requests as r
from lxml import etree
import pandas as pd
import os

# 下載並快取 TWSE 股票清單（含過濾下市與非法代碼）
def twse_stock_info(cache_file="twse_stock.csv", use_cache=True):
    if use_cache and os.path.exists(cache_file):
        print(f"📦 使用快取資料：{cache_file}")
        return pd.read_csv(cache_file, dtype=str)

    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    res = r.get(url)
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