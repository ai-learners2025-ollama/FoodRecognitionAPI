import os
import uuid
from datetime import datetime
from django.conf import settings

def uploaded_image(image_file, save_dir: str = "outputs"):
    if image_file is None:
        return None, None

    save_dir = os.path.join(settings.BASE_DIR, save_dir)
    # 儲存目錄：依日期建立
    date_str = datetime.now().strftime('%Y-%m-%d')
    folder_original = os.path.join(settings.BASE_DIR, f'{save_dir}/{date_str}/original/')
    os.makedirs(folder_original, exist_ok=True)

    # 產生唯一檔名
    ext = os.path.splitext(image_file.name)[1]
    uid = uuid.uuid4().hex
    filename = f"{uid}{ext}"
    original_path = os.path.join(folder_original, filename)

    # 儲存原圖
    with open(original_path, 'wb+') as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    # 傳回檔名與原圖存放資料夾
    return filename, folder_original



