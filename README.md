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

## ⏱️ 自動排程

## 🪟 Windows：使用工作排程器 + `run_main.bat`

### ✅ 已提供批次檔案：`run_main.bat`

內容如下：

```bat
@echo off
cd /d C:\Users\你的使用者名稱\路徑\Stock_TWSE
python main.py
```

### ✅ 設定步驟：

1. 開啟「工作排程器」→ 建立新工作
2. 【觸發條件】設定為每天固定時間（如早上 8:00）
3. 【動作】選擇「啟動程式」，指定 `run_main.bat` 的完整路徑
4. 【一般】勾選「以最高權限執行」
5. 儲存並啟用即可每日自動執行

---

## 🍎 macOS / 🐧 Linux：使用 crontab + `run_main.sh`

### ✅ 已提供 shell 腳本：`run_main.sh`

檔案內容如下：

```bash
#!/bin/bash
cd /home/your_username/your_project/
python3 main.py
```

如使用虛擬環境，請啟用虛擬環境再執行程式：

```bash
source venv/bin/activate
python3 main.py
```

### ✅ 設定排程：

1. 開啟終端機
2. 執行命令：

```bash
crontab -e
```

3. 加入以下排程設定（每天早上 8 點執行）：

```bash
0 8 * * * /bin/bash /home/your_username/your_project/run_main.sh >> /home/your_username/your_project/run.log 2>&1
```

4. 儲存並離開編輯器，排程即自動生效

---

## 📁 注意事項：

- `run_main.bat` 與 `run_main.sh` 均需位於你的專案根目錄或指定正確路徑
- 建議腳本內使用完整絕對路徑，避免排程器找不到目錄
- 輸出報表與圖表會自動儲存在 `charts/` 和根目錄中

---

## 📌 推薦測試方式

- 在設定排程前，請先手動執行腳本確認無誤：
    - Windows：雙擊 `run_main.bat`
    - Linux/macOS：執行 `bash run_main.sh`

---

## 🧠 小提醒：

- Linux 系統請確認 `run_main.sh` 權限正確，可執行：
```bash
chmod +x run_main.sh
```

- 若 Python 環境需特殊設定（如 conda/venv），請在腳本中加入 activate 指令

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

- [【Python股市爬蟲 第3集】一口氣爬多檔台股個股｜必學的股市爬蟲技術](https://www.youtube.com/watch?v=wM5wJNgpIbA&ab_channel=%E8%82%A1%E6%B5%B7%E5%B0%8F%E8%8B%B1%E9%9B%84)
- [一口氣下載多支上市台股個股歷史資料 Colab程式碼](https://colab.research.google.com/drive/1gSpB7NWEUu7gOv53c6VQsO0E3jUqUreo?usp=sharing)
- [台灣證券交易所官方網站 (TWSE)](https://www.twse.com.tw/)
- [Google Fonts: Noto Sans CJK](https://fonts.google.com/noto#sans-hant)
- [scikit-learn 官方文件](https://scikit-learn.org/)
- [Matplotlib 中文字體處理](https://matplotlib.org/)
- [pandas 中文手冊](https://pandas.pydata.org/)
