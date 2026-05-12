# PythonAnywhere 部署步驟

## 帳號與網址資訊
- **Admin 帳號**: cmlin
- **Admin 密碼**: 12345678
- **網站網址**: https://[你的帳號].pythonanywhere.com

---

## 步驟一：上傳專案

### 方法 A：使用 Git（推薦）
```bash
# 在 PythonAnywhere Bash console 執行
git clone https://github.com/[你的帳號]/fengyun_inn.git
```

### 方法 B：壓縮上傳
1. 將整個 `fengyun_inn/` 資料夾壓縮成 zip
2. 在 PythonAnywhere Files 頁面上傳
3. 在 Bash console 解壓縮：
```bash
unzip fengyun_inn.zip
```

---

## 步驟二：建立虛擬環境

```bash
# 在 PythonAnywhere Bash console
mkvirtualenv fengyun_env --python=python3.10
workon fengyun_env
pip install -r ~/fengyun_inn/requirements.txt
```

---

## 步驟三：初始化資料庫

```bash
cd ~/fengyun_inn
python manage.py migrate
python manage.py loaddata main/fixtures/initial_data.json
python create_superuser.py
python manage.py collectstatic --noinput
```

---

## 步驟四：設定 Web App

1. 進入 **Web** 頁面，點擊 **Add a new web app**
2. 選擇 **Manual configuration**，Python 版本選 **3.10**
3. 設定以下項目：

### Source code:
```
/home/[你的帳號]/fengyun_inn
```

### Working directory:
```
/home/[你的帳號]/fengyun_inn
```

### Virtualenv:
```
/home/[你的帳號]/.virtualenvs/fengyun_env
```

### WSGI configuration file:
點擊 WSGI file 連結，將內容改為：
```python
import sys
import os

path = '/home/[你的帳號]/fengyun_inn'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'fengyun_inn.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

## 步驟五：設定靜態檔案

在 Web 頁面 **Static files** 區塊加入：

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/[你的帳號]/fengyun_inn/staticfiles` |
| `/media/` | `/home/[你的帳號]/fengyun_inn/media` |

---

## 步驟六：修改 settings.py（重要）

```bash
cd ~/fengyun_inn
nano fengyun_inn/settings.py
```

修改以下設定：
```python
DEBUG = False  # 改為 False
ALLOWED_HOSTS = ['[你的帳號].pythonanywhere.com']
```

---

## 步驟七：Reload 並測試

1. 點擊 **Reload** 按鈕
2. 開啟 `https://[你的帳號].pythonanywhere.com`
3. 測試 admin 後台：`https://[你的帳號].pythonanywhere.com/admin/`
   - 帳號：**cmlin**
   - 密碼：**12345678**

---

## 常見問題

### 靜態檔案無法載入
確認已執行 `python manage.py collectstatic --noinput`

### 500 Internal Server Error
查看 PythonAnywhere error log：
```bash
cat /var/log/[你的帳號].pythonanywhere.com.error.log
```

### 資料庫錯誤
```bash
cd ~/fengyun_inn
python manage.py migrate --run-syncdb
```
