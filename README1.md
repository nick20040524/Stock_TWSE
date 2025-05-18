
# 台灣上市股票每日更新與收盤價預測系統 📈

本專案可自動擷取台灣證券交易所（TWSE）股票資料，更新歷史數據，並使用機器學習模型進行**收盤價預測**與**漲跌預測**，每日自動更新、產出報告與圖表。

---

## 📦 功能簡介

- 自動抓取 TWSE 上市股票資料
- 快取歷史資料 fallback 檔案（`fallback_XXXX.csv`）
- 預測明日收盤價（回歸模型）
- 預測明日漲跌方向（分類模型）
- 每支股票個別產出圖表：`charts/price_prediction_XXXX.png`
- 匯出 Excel 報表：`prediction_report.xlsx`
- 支援每日自動排程更新

---

## 🚀 安裝方式

### 1️⃣ 安裝套件

請先安裝必要的 Python 套件：

```bash
pip install -r requirements.txt
```

### 2️⃣ 下載中文字體

- ✅ **Windows/macOS**：系統已內建常見中文字體（如微軟正黑體、蘋方），無需額外安裝。
- 🐧 **Ubuntu/Linux**：請安裝 `fonts-noto-cjk` 以避免中文亂碼：

```bash
sudo apt install fonts-noto-cjk
```

---

## 🛠️ 使用方式

### ▶️ 執行主程式

```bash
python main.py
```

執行後將會：
- 更新 TWSE 股價資料
- 執行預測
- 匯出圖表與 Excel 報表

---

## ⏱️ 自動排程

### Linux/macOS (使用 crontab)

```bash
crontab -e
```

加入以下排程（每天早上 8:00 執行）：

```bash
0 8 * * * /usr/bin/python3 /your/path/main.py >> /your/path/run.log 2>&1
```

### Windows (使用工作排程器 + .bat)

建立 `run_main.bat`：

```bat
@echo off
cd /d C:\你的\專案\目錄
python main.py
```

並透過「工作排程器」設定每日自動執行。

---

## 📁 專案結構

```
.
├── main.py                       # 主程式入口
├── requirements.txt              # 所需套件
├── README.md
├── stock/                        # 自定義模組
│   ├── __init__.py
│   ├── setup_chinese_font.py
│   ├── twse_stock_info.py
│   ├── update_module.py
│   └── predict_and_export.py
├── fallback_2330.csv             # 快取歷史資料
├── prediction_report.xlsx        # 預測報表
├── charts/
│   ├── price_prediction_2330.png
│   ├── ...
```

---

## 👨‍💻 作者

徐景煌 @ National Ilan University  
電子工程系 | 股票爬蟲與預測專案

---

## 📜 License

本專案開源，僅供學術與研究用途使用。

---

## 📚 參考資料

- [台灣證券交易所官方網站 (TWSE)](https://www.twse.com.tw/)
- [Google Fonts: Noto Sans CJK](https://www.google.com/get/noto/#sans-hant)
- [scikit-learn 官方文件](https://scikit-learn.org/stable/)
- [Matplotlib 圖表官方教學](https://matplotlib.org/stable/users/index.html)
- [pandas 中文手冊](https://pandas.pydata.org/docs/)
