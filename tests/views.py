from django.shortcuts import render
from PIL import Image
from modules.aimodels import cnn, yolo
from django.http import HttpResponseBadRequest
from utils import image_utils, models_utils
# from modules.aimodels.yolo import detect_image, query_food_infos, sum_nutrition

def test(request):
    if request.method == 'GET':
        return render(request, 'pages/test.html')
    else: 
        img = Image.open(request.FILES.get('image'))

        # 主分類（英文）
        result = cnn.classifyFood(img)

        # YOLO 偵測
        path, predictions = yolo.detect_image(img)

        # 查詢營養資訊 + 主分類中文
        food_infos, food_zh = yolo.query_food_infos(result, predictions)

        summary = yolo.sum_nutrition(food_infos)

         # ✅ 移除主分類，只保留 is_main=False 的項目（食材）
        food_infos = [info for info in food_infos if not info.get("is_main")]
        
        return render(request, 'pages/test.html', {
            'result': result,           # 英文主分類
            'food_zh': food_zh,         # 中文主分類
            'food_infos': food_infos,   # 食材 + 主分類列表
            'summary': summary,         # 總營養
        })


def test2(request):
    if request.method == 'GET':
        return render(request, 'pages/test2.html')
    else: 
        image_file = request.FILES.get('image')
        if not image_file:
            return render(request, 'pages/test2.html',{"result":"請先上傳圖片"})
        
        # 取IP
        ip_address = models_utils.get_client_ip(request)  # 你需要另外定義這個函式

        # 取食物模型
        # model_id1, model_file1 = models_utils.get_enabled_model(1)
        model_id1 = 1

        # 儲存圖檔
        filename, folder_original = image_utils.uploaded_image(image_file)

        img = Image.open(image_file)

        # 主分類（英文）
        result = cnn.classifyFood(img)
        # 存Log
        models_utils.save_recog_log(
            filename=filename,
            date_str=folder_original,          
            recog_model_id=model_id1,
            model_type=1,
            ip_address=ip_address,
            recog_image_name="",
            recog_content=result
        )

        # YOLO 偵測
        # 取食材模型
        # model_id2, model_file2 = models_utils.get_enabled_model(2)
        model_id2 = 2
        path, predictions = yolo.detect_image(folder_original)

        # 查詢營養資訊 + 主分類中文
        food_infos, food_zh = yolo.query_food_infos(result, predictions)

        summary = yolo.sum_nutrition(food_infos)

        # ✅ 移除主分類，只保留 is_main=False 的項目（食材）
        food_infos = [info for info in food_infos if not info.get("is_main")]
        
        # 存Log        
        models_utils.save_recog_log(
            filename=filename,
            date_str=path,
            recog_model_id=model_id2,
            model_type=2,
            ip_address=ip_address,
            recog_image_name=path,
            recog_content=predictions
        )


        return render(request, 'pages/test2.html', {
            'result': result,           # 英文主分類
            'food_zh': food_zh,         # 中文主分類
            'food_infos': food_infos,   # 食材 + 主分類列表
            'summary': summary,         # 總營養
        })
        
        

