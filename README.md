# 🇹🇼 台灣上市股票資料更新與收盤價預測系統 📈

本專案可自動擷取台灣證券交易所（TWSE）上市股票資訊，更新歷史股價資料，並使用機器學習模型進行每日收盤價與漲跌方向預測。  
支援快取機制與 SSL 憑證繞過，適合部署於開發環境與自動排程。

---

## 🔧 功能說明

- ✅ 擷取最新 TWSE 上市股票清單（含快取）
- ✅ 抓取個股每日歷史資料（fallback_{代碼}.csv）
- ✅ 預測明日收盤價（回歸模型）
- ✅ 預測明日漲跌方向（分類模型）
- ✅ 產出圖表（charts/price_prediction_{代碼}.png）
- ✅ 匯出預測報告（prediction_report.xlsx）
- ✅ 支援 SSL 繞過與 fallback 快取（避免網路錯誤）

---

## 📁 專案結構

```
Stock_TWSE/
├── main.py                          # 主程式（設定、流程控制）
├── requirements.txt                 # 相依套件
├── twse_stock.csv                   # 股票清單快取（自動產生）
├── prediction_report.xlsx           # 預測摘要報告
├── charts/                          # 預測圖表資料夾
│   └── price_prediction_2330.png
├── fallback_2330.csv                # 台積電歷史資料快取（自動產生）
├── stock/                           # 模組資料夾
│   ├── __init__.py
│   ├── setup_chinese_font.py        # 中文字體設定（matplotlib）
│   ├── twse_stock_info.py           # 股票清單擷取與快取
│   ├── update_module.py             # 歷史股價更新模組（含 verify_ssl 控制）
│   └── predict_and_export.py        # 預測與圖表、報表輸出
```

---

## 🛠️ 安裝與執行方式

### 1️⃣ 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 2️⃣ 建議安裝中文字體（Linux 系統）

```bash
sudo apt install fonts-noto-cjk
```

---

## ▶️ 執行主程式

```bash
python main.py
```

程式會自動：

- 擷取或使用快取股票清單
- 更新歷史資料（fallback_xxxx.csv）
- 執行預測（分類 + 回歸）
- 產出圖表與報表

---

## 🔐 SSL 憑證問題（開發環境常見）

若遇到以下錯誤：

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

可於 `main.py` 設定以下變數以跳過驗證（僅用於測試）：

```python
verify_ssl = False
```

並將此參數傳入：

```python
twse_stock_info(use_cache=False, verify_ssl=verify_ssl)
update_stock_data_incrementally(..., verify_ssl=verify_ssl)
```

---

## ⏱️ 自動排程建議

### Windows 任務排程器

建立 `run_main.bat`：

```bat
@echo off
cd /d C:\你的\資料夾路徑
python main.py
```

---

## 👨‍💻 作者資訊

徐景煌 @ 國立宜蘭大學  
電子工程系 | 股票預測與爬蟲專案開發者  

---

## 📜 授權條款

本專案開源、僅供學術與研究用途。  
若引用請附上原始來源與作者。

---

## 📚 資源參考

- [台灣證券交易所 TWSE](https://www.twse.com.tw/)
- [scikit-learn 官方文件](https://scikit-learn.org/)
- [matplotlib 中文字體處理](https://matplotlib.org/)
- [pandas 中文手冊](https://pandas.pydata.org/)
