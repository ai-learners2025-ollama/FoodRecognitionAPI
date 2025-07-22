import os
import uuid
import base64
from datetime import datetime
from django.conf import settings


def uploaded_image(image_file):
    try:
        if image_file is None:
            return None, None, None

        # 儲存目錄：依日期建立
        date_str = datetime.now().strftime('%Y_%m')
        folder_original = os.path.join(settings.MEDIA_IMAGE, date_str, 'original')
        os.makedirs(folder_original, exist_ok=True)

        # 產生唯一檔名
        ext = os.path.splitext(image_file.name)[1]
        uid = uuid.uuid4().hex
        filename = f"{uid}{ext}"

        # 圖片儲存實體完整路徑
        original_path = os.path.join(folder_original, filename)

        with open(original_path, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # 回傳圖片相對路徑（用於 URL）
        relative_path = os.path.join(settings.MEDIA_IMAGE_URL, date_str, 'original', filename).replace('\\', '/')
        return filename, original_path, relative_path
    except Exception as e:
        print(f"[uploaded_image] 儲存錯誤：{e}")
        return None, None, None





def uploaded_base64_image(image_data: str):
    """
    儲存 base64 圖片資料為實體檔案
    :param image_data: base64 編碼字串（例如 'data:image/jpeg;base64,...'）
    :return: (filename, original_path, relative_path)
    """
    try:
        if not image_data.startswith('data:image'):
            return None, None, None

        # 儲存目錄：依日期建立
        date_str = datetime.now().strftime('%Y_%m')
        folder_original = os.path.join(settings.MEDIA_IMAGE, date_str, 'original')
        os.makedirs(folder_original, exist_ok=True)
        
        # 解析格式與資料
        format, imgstr = image_data.split(';base64,')  
        ext = format.split('/')[-1]  # 副檔名：jpg / png / etc
        filename = f"{uuid.uuid4()}.{ext}"

        # 完整儲存路徑
        original_path = os.path.join(folder_original, filename)

        # 寫入檔案
        with open(original_path, 'wb') as f:
            f.write(base64.b64decode(imgstr))

        # 回傳圖片相對路徑（用於 URL）
        relative_path = os.path.join(settings.MEDIA_IMAGE_URL, date_str, 'original', filename).replace('\\', '/')
        return filename, original_path, relative_path

    except Exception as e:
        print(f"[uploaded_base64_image] 儲存錯誤：{e}")
        return None, None, None


