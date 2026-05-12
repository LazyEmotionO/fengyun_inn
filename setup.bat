@echo off
echo ========================================
echo 風雲客棧 Django 專案 初始化設定
echo ========================================

echo [1/5] 安裝套件...
pip install -r requirements.txt

echo [2/5] 建立資料庫 migrations...
python manage.py makemigrations main
python manage.py migrate

echo [3/5] 載入初始資料...
python manage.py loaddata main/fixtures/initial_data.json

echo [4/5] 收集靜態檔案...
python manage.py collectstatic --noinput

echo [5/5] 建立管理員帳號...
echo 請手動執行: python manage.py createsuperuser
echo 帳號設定為: cmlin / 12345678

echo ========================================
echo 設定完成！執行以下指令啟動網站：
echo python manage.py runserver
echo ========================================
pause
