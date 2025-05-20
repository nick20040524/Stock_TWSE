# -*- coding: utf-8 -*-
import pandas as pd
import os
import matplotlib.pyplot as plt
import joblib
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# 資料讀取
def load_stock_data(stock_code, fallback_dir="."):
    path = os.path.join(fallback_dir, f"fallback_{stock_code}.csv")
    if not os.path.exists(path):
        print(f"❌ 找不到 fallback_{stock_code}.csv")
        return None
    df = pd.read_csv(path, parse_dates=["日期"])
    df = df.dropna(subset=["收盤價", "成交股數"])
    df["股票代碼"] = stock_code
    return df

# 特徵建構
# 從 fallback 目錄讀取指定股票代碼的歷史資料（CSV），並過濾掉無效欄位（收盤價與成交股數缺值）
def build_features(df):
    df = df.copy()
    df["收盤價_shift1"] = df["收盤價"].shift(1)
    df["漲跌價差_shift1"] = df["漲跌價差"].shift(1)
    df["收盤_5日均線"] = df["收盤價"].rolling(5).mean()
    df["收盤價明日"] = df["收盤價"].shift(-1)
    df["漲跌標籤"] = (df["收盤價明日"] > df["收盤價"]).astype(int)
    return df.dropna()

# 模型訓練與儲存模型
def train_and_predict(df_feat, stock_code):
    features = ["收盤價_shift1", "漲跌價差_shift1", "成交股數", "收盤_5日均線"]
    X = df_feat[features]
    y_reg = df_feat["收盤價明日"]

    if len(df_feat) < 20:
        print(f"⚠️ {stock_code} 資料過少，跳過訓練")
        return pd.DataFrame()

    df_feat = df_feat.reset_index(drop=True)
    X = X.reset_index(drop=True)
    y_reg = y_reg.reset_index(drop=True)

    X_train, X_test, y_train, y_test = train_test_split(X, y_reg, test_size=0.2, shuffle=False)

    reg_model = LinearRegression()
    reg_model.fit(X_train, y_train)

    # 儲存模型
    os.makedirs("models", exist_ok=True)
    model_path = f"models/model_{stock_code}.pkl"
    joblib.dump(reg_model, model_path)
    print(f"💾 已訓練並儲存模型：{model_path}")

    y_pred = reg_model.predict(X_test)

    df_result = df_feat.iloc[X_test.index].copy()
    df_result["預測收盤價"] = y_pred
    df_result["預測漲跌"] = (y_pred > df_result["收盤價"]).astype(int)
    df_result["信心度"] = (1 - abs(y_pred - df_result["收盤價"]) / df_result["收盤價"]).clip(0, 1)
    return df_result

# 模型載入與推論
def load_model_and_predict(df_feat, stock_code):
    model_path = f"models/model_{stock_code}.pkl"
    if not os.path.exists(model_path):
        print(f"❌ 找不到模型：{model_path}")
        return pd.DataFrame()

    reg_model = joblib.load(model_path)
    print(f"📥 載入模型：{model_path}")

    features = ["收盤價_shift1", "漲跌價差_shift1", "成交股數", "收盤_5日均線"]
    X = df_feat[features].reset_index(drop=True)
    df_feat = df_feat.reset_index(drop=True)

    y_pred = reg_model.predict(X)
    df_result = df_feat.copy()
    df_result["預測收盤價"] = y_pred
    df_result["預測漲跌"] = (y_pred > df_result["收盤價"]).astype(int)
    df_result["信心度"] = (1 - abs(y_pred - df_result["收盤價"]) / df_result["收盤價"]).clip(0, 1)
    return df_result

# 統一入口：先檢查模型是否存在
def ensure_model_and_predict(df_feat, stock_code):
    model_path = f"models/model_{stock_code}.pkl"
    if os.path.exists(model_path):
        return load_model_and_predict(df_feat, stock_code)
    else:
        return train_and_predict(df_feat, stock_code)

# 多支股票批次預測
def predict_multiple_stocks(stock_codes):
    all_results = []
    for code in stock_codes:
        df = load_stock_data(code)
        if df is None:
            continue
        df_feat = build_features(df)
        df_pred = ensure_model_and_predict(df_feat, stock_code=code)
        df_pred["股票代碼"] = code
        all_results.append(df_pred)
    return pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()

# 預測結果圖表輸出(預測日往前算10天)
def plot_predictions_ten(df_result, output_dir=".", prop=None):
    os.makedirs(output_dir, exist_ok=True)
    grouped = df_result.groupby("股票代碼")

    for code, group in grouped:
        last_date = group["日期"].max()
        pred_date = last_date + timedelta(days=1)

        # 過濾：預測日前 10 天到預測日
        start_date = pred_date - timedelta(days=10)
        df_zoom = group[(group["日期"] >= start_date) & (group["日期"] <= pred_date)].copy()

        if df_zoom.empty:
            print(f"⚠️ {code} 在預測日前 10 天內沒有資料，跳過圖表")
            continue

        plt.figure(figsize=(10, 5))
        plt.plot(df_zoom["日期"], df_zoom["收盤價"], label="實際收盤價", alpha=0.8)
        plt.plot(df_zoom["日期"], df_zoom["預測收盤價"], linestyle='--', label="預測收盤價", alpha=0.8)
        plt.axvline(pred_date, color="red", linestyle=":", label="預測日")
        plt.xticks(rotation=45)

        stock_name = df_zoom["有價證券代號名稱"].iloc[0]
        title = f"{code} {stock_name} 收盤價趨勢（預測日前10天）"
        plt.title(title, fontproperties=prop)
        plt.xlabel("日期", fontproperties=prop)
        plt.ylabel("收盤價", fontproperties=prop)
        plt.xticks(fontproperties=prop)
        plt.yticks(fontproperties=prop)
        plt.legend(prop=prop)
        plt.grid(True)
        plt.tight_layout()

        filename = os.path.join(output_dir, f"price_prediction_{code}_ten.png")
        plt.savefig(filename)
        print(f"📈 已儲存圖檔：{filename}")
        plt.close()

# 預測結果圖表輸出(上市日至預測日)
def plot_predictions_all(df_result, output_dir=".", prop=None):
    os.makedirs(output_dir, exist_ok=True)
    grouped = df_result.groupby("股票代碼")
    for code, group in grouped:
        plt.figure(figsize=(10, 5))
        plt.plot(group["日期"], group["收盤價"], label="實際收盤價", alpha=0.8)
        plt.plot(group["日期"], group["預測收盤價"], linestyle='--', label="預測收盤價", alpha=0.8)
        plt.xticks(rotation=45)

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

        filename = os.path.join(output_dir, f"price_prediction_{code}_all.png")
        plt.savefig(filename)
        print(f"📈 已儲存圖檔：{filename}")
        plt.close()

# 預測摘要報告輸出
def export_prediction_summary(df_result, output_path="prediction_report.xlsx"):
    today_str = datetime.today().strftime("%Y/%m/%d")
    latest = df_result.sort_values("日期").groupby("股票代碼").tail(1).copy()
    latest["預測日期"] = latest["日期"] + timedelta(days=1)
    latest["預測日期"] = latest["預測日期"].dt.strftime("%Y/%m/%d")
    latest["今天日期"] = today_str
    latest["漲跌結果"] = latest["預測漲跌"].map({1: "↑ 漲", 0: "↓ 跌"})
    latest["信心度"] = (latest["信心度"] * 100).round(2).astype(str) + "%"
    latest["開盤日"] = latest["日期"].dt.strftime("%Y/%m/%d")

    summary = latest[[
        "今天日期", "預測日期", "開盤日", "股票代碼", "有價證券代號名稱",
        "收盤價", "預測收盤價", "漲跌結果", "信心度"
    ]].copy()

    summary["收盤價"] = summary["收盤價"].round(2)
    summary["預測收盤價"] = summary["預測收盤價"].round(2)
    summary.to_excel(output_path, index=False)
    print(f"📊 預測報告已輸出至：{output_path}")
