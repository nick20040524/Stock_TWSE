# -*- coding: utf-8 -*-
url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'

def twse_stock_info():
    # 下載上市證券國際證券辨識號碼一覽表
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    res = r.get(url)
    res.encoding = 'big5' #確保繁體中文字正常解析
    root = etree.HTML(res.text)
    data = root.xpath('//tr')[1:]

    # 設定DataFrame儲存資料
    df = pd.DataFrame(columns = ["上市有價證券種類", "有價證券代號代碼", "有價證券代號名稱", "國際證券辨識號碼(ISIN Code", "上市日", "市場別", "產業別", "CFICode", "備註"])

    # 將資料一行一行存入DataFrame內
    category = ''
    row_num = 0
    for row in data:
        row = list(map(lambda x: x.text, row.iter()))[1:]
        if len(row) == 3:
            category = row[1].strip(' ')
        else:
            stock_code, stock_name = row[0].split('\u3000')
            data_row = [category, stock_code, stock_name, row[1], row[2], row[3], row[4], row[5], row[6]]
            df.loc[row_num] = data_row
            row_num += 1
    return df