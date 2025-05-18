# -*- coding: utf-8 -*-
import pandas as pd
import os
import matplotlib.pyplot as plt
from IPython.display import display
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score

def load_stock_data(stock_code, fallback_dir="."):
    path = os.path.join(fallback_dir, f"fallback_{stock_code}.csv")
    if not os.path.exists(path):
        print(f"❌ 找不到 fallback_{stock_code}.csv")
        return None
    df = pd.read_csv(path, parse_dates=["日期"])
    df = df.dropna(subset=["收盤價", "成交股數"])
    df["股票代碼"] = stock_code
    return df

def build_features(df):
    df = df.copy()
    df["收盤價_shift1"] = df["收盤價"].shift(1)
    df["漲跌價差_shift1"] = df["漲跌價差"].shift(1)
    df["收盤_5日均線"] = df["收盤價"].rolling(5).mean()
    df["收盤價明日"] = df["收盤價"].shift(-1)
    df["漲跌標籤"] = (df["收盤價明日"] > df["收盤價"]).astype(int)
    return df.dropna()

def train_and_predict(df_feat):
    features = ["收盤價_shift1", "漲跌價差_shift1", "成交股數", "收盤_5日均線"]
    X = df_feat[features]
    y_reg = df_feat["收盤價明日"]
    y_cls = df_feat["漲跌標籤"]

    if len(df_feat) < 20:
        print("⚠️ 資料過少，跳過訓練")
        return pd.DataFrame()

    df_feat = df_feat.reset_index(drop=True)
    X = X.reset_index(drop=True)
    y_reg = y_reg.reset_index(drop=True)
    y_cls = y_cls.reset_index(drop=True)

    X_train, X_test, y_train_r, y_test_r = train_test_split(X, y_reg, test_size=0.2, shuffle=False)
    _, _, y_train_c, y_test_c = train_test_split(X, y_cls, test_size=0.2, shuffle=False)

    reg_model = LinearRegression()
    reg_model.fit(X_train, y_train_r)
    y_pred_reg = reg_model.predict(X_test)

    cls_model = RandomForestClassifier(n_estimators=100, random_state=0)
    cls_model.fit(X_train, y_train_c)
    y_pred_cls = cls_model.predict(X_test)
    y_pred_prob = cls_model.predict_proba(X_test)

    # 取每個樣本預測類別的最大機率作為信心度
    confidence = y_pred_prob.max(axis=1)  # 最大的那一欄（機率值）

    df_result = df_feat.iloc[X_test.index].copy()
    df_result["預測收盤價"] = y_pred_reg
    df_result["預測漲跌"] = y_pred_cls
    df_result["實際漲跌"] = y_test_c.values
    df_result["信心度"] = confidence
    return df_result

def predict_multiple_stocks(stock_codes):
    all_results = []
    for code in stock_codes:
        df = load_stock_data(code)
        if df is None:
            continue
        df_feat = build_features(df)
        df_pred = train_and_predict(df_feat)
        df_pred["股票代碼"] = code
        all_results.append(df_pred)
    return pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()

def plot_predictions(df_result, output_dir=".", prop=None):
    os.makedirs(output_dir, exist_ok=True)

    grouped = df_result.groupby("股票代碼")
    for code, group in grouped:
        plt.figure(figsize=(10, 5))
        plt.plot(group["日期"], group["收盤價"], label="實際收盤價", alpha=0.8)
        plt.plot(group["日期"], group["預測收盤價"], linestyle='--', label="預測收盤價", alpha=0.8)

        stock_name = group["有價證券代號名稱"].iloc[0]
        title = f"{code} {stock_name} 收盤價預測"
        plt.title(title, fontproperties=prop)
        plt.xlabel("日期", fontproperties=prop)
        plt.ylabel("收盤價", fontproperties=prop)
        plt.xticks(fontproperties=prop)
        plt.yticks(fontproperties=prop)
        plt.legend(prop=prop)
        plt.grid(True)
        plt.tight_layout()

        filename = os.path.join(output_dir, f"price_prediction_{code}.png")
        plt.savefig(filename)
        print(f"📈 已儲存圖檔：{filename}")
        plt.close()

def export_prediction_summary(df_result, output_path="prediction_report.xlsx"):
    today_str = datetime.today().strftime("%Y/%m/%d")

    # 取得每支股票最後一筆預測
    latest = df_result.sort_values("日期").groupby("股票代碼").tail(1).copy()

    # 計算預測日期：預設為最後日期 + 1 天
    latest["預測日期"] = latest["日期"] + timedelta(days=1)
    latest["預測日期"] = latest["預測日期"].dt.strftime("%Y/%m/%d")
    latest["今天日期"] = today_str

    # 漲跌符號與百分比
    latest["漲跌結果"] = latest["預測漲跌"].map({1: "↑ 漲", 0: "↓ 跌"})
    latest["信心度"] = (latest["信心度"] * 100).round(2).astype(str) + "%"

    summary = latest[[
        "今天日期", "預測日期", "股票代碼", "有價證券代號名稱",
        "收盤價", "預測收盤價", "漲跌結果", "信心度"
    ]].copy()

    summary["收盤價"] = summary["收盤價"].round(2)
    summary["預測收盤價"] = summary["預測收盤價"].round(2)

    summary.to_excel(output_path, index=False)
    print(f"📊 預測報告已輸出至：{output_path}")