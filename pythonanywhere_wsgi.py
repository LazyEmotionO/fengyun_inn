# =====================================================
# PythonAnywhere WSGI 設定檔
# 複製此檔案內容至 PythonAnywhere WSGI 設定頁
# =====================================================
import sys
import os

# 替換 'yourusername' 為你的 PythonAnywhere 帳號名稱
# 替換 'fengyun_inn' 為你的專案資料夾名稱

path = '/home/yourusername/fengyun_inn'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'fengyun_inn.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
