REM for Windows 環境
@echo off

REM 將目前目錄切換到你的專案資料夾
cd /d C:\Users\YourName\your_project

REM 如果你有使用虛擬環境，請先啟用它
REM call venv\Scripts\activate

REM 執行主程式 main.py
python main.py

REM 將結果輸出到 log 檔案（可選）
REM python main.py >> run.log 2>&1
