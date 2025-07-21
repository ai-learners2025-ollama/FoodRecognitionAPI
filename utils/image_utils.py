import os
import uuid
from datetime import datetime
from django.conf import settings

def uploaded_image(image_file, save_dir: str = "models/"):
    if image_file is None:
        return None, None

    # 儲存目錄：依日期建立
    date_str = datetime.now().strftime('%Y_%m')
    folder_original = os.path.join(settings.MEDIA_ROOT, save_dir, date_str)
    os.makedirs(folder_original, exist_ok=True)

    # 產生唯一檔名
    ext = os.path.splitext(image_file.name)[1]
    uid = uuid.uuid4().hex
    filename = f"{uid}{ext}"

    # 圖片儲存實體完整路徑
    original_path = os.path.join(folder_original, filename)

    # 儲存圖片
    with open(original_path, 'wb+') as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    # 回傳圖片相對路徑（用於 URL）
    relative_path = os.path.join(save_dir, date_str, filename).replace('\\', '/')
    return filename, relative_path, original_path



