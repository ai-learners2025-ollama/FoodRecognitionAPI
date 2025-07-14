# Django Blog

## 打包 django 套件集
```shell
pip freeze > requirements.txt
```

## 建立 Django apache 環境 (ubuntu24.04-lts_x86)
```shell
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install apache2 libapache2-mod-wsgi-py3
sudo apt install -y software-properties-common build-essential libffi-dev libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev libssl-dev
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12
sudo apt install python3-pip python3-venv
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
# 綁定 python 為 python3.12
python -V

# 建立虛擬環境
python -m venv ~/django_env
source ~/django_env/bin/activate
pip install -r ~/djangoBLOG/requirements.txt
# 如果出現錯誤
pip install django==4.2 && pip install markdown
# 可以用指令檢查安裝狀態 
pip list  
#檢查 Django 版本
django-admin version

# 啟動遠端的測試伺服器
cd ~/djangoBLOG
python manage.py runserver 0.0.0.0:8000

# 產生對應資料庫結構 (無資料)
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## 部署GCP
```shell
sudo cp chunyen.learnai2025.com.conf /etc/apache2/sites-available

# 檢查檔案
ls -la /etc/apache2/sites-available/
# 啟用設定
sudo a2ensite chunyen.learnai2025.com.conf
sudo systemctl reload apache2
# 調整權限
sudo chmod +x /home/everfortune_jay
sudo chown :www-data ~/djangoBLOG
sudo chown :www-data ~/djangoBLOG/DjangoBlog
sudo systemctl reload apache2


# 使用指令蒐集靜態資源
# 將static 檔案打包到 public下
python manage.py collectstatic

# 如果忘記資料庫密碼
# 建立超級使用者
python manage.py createsuperuser
#修改密碼 
python manage.py changepassword <使用者名字>
# 修改權限資料庫權限
sudo chmod 664 ~/djangoBLOG/db.sqlite3
sudo chown :www-data ~/djangoBLOG/db.sqlite3

#錯誤訊息的判讀
#查看 apache2 狀態
sudo systemctl status apache2

#查看 apache2 錯誤訊息
journalctl -xeu apache2.service

#系統層級的紀錄
ls -la /var/log/apache2/
cat /var/log/apache2/error-djangoBLOG.log
nano /var/log/apache2/error-djangoBLOG.log
```