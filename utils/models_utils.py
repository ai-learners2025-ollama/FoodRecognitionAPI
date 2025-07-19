from food_recognition.models import RecogLog, RecogModel
from datetime import datetime
import base64

def get_enabled_model(model_type: int = 1):
    """
    取得第一筆 is_enabled=True 且指定 model_type 的 RecogModel 資料
    回傳 (recog_model_id, model_type)，若無資料或發生錯誤則回傳 (None, None)
    """
    try:
        recog_model = RecogModel.objects.filter(model_type=model_type, is_enabled=True).first()
        if recog_model:
            return recog_model.id, recog_model.model_file
        else:
            return None, None
    except Exception as e:
       
        return None, None



def save_recog_log(
    filename: str,
    date_str: str,
    recog_model_id: int,
    model_type: int,
    ip_address: str,
    recog_image_name: str = "",
    recog_content: str = "",
):
    try:
        """
        將辨識紀錄儲存至 RecogLog 資料表
        """
        RecogLog.objects.create(
            image_name=filename,
            image_path=date_str,
            recog_image_name=recog_image_name,
            recog_content=recog_content,
            recog_model_id=recog_model_id,
            model_type=model_type,
            create_ip=ip_address,
            create_date=datetime.now()
        )
        return True
    except Exception as e:
       
        return False
    


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')




def image_to_base64(image_path: str) -> str:
    """
    將圖片檔案轉成 Base64 字串，回傳 HTML 可用的格式。
    參數: image_path - 圖片的絕對路徑
    """
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        ext = image_path.split('.')[-1].lower()
        return f"data:image/{ext};base64,{encoded_string}"


