import os
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
    # try:
       if request.method == 'GET':
            return render(request, 'pages/test2.html')
       else: 
            # image_file = request.FILES.get('image')
            image_src = request.POST.get('image_src')  # 這裡會是 base64 字串
            if not image_src:
                return render(request, 'pages/test2.html',{"result":"請先上傳圖片"})
            
            # 取IP
            ip_address = models_utils.get_client_ip(request)  # 你需要另外定義這個函式

            # 儲存圖檔
            # filename, original_path, relative_path = image_utils.uploaded_image(image_file)
            filename, original_path, relative_path = image_utils.uploaded_base64_image(image_src)

            img = Image.open(original_path)
            img = img.convert('RGB')  #  RGB 格式
            
            # 取食物模型
            model1 = models_utils.get_enabled_model(1)

            # 主分類（英文）
            result = cnn.classifyFood(img, model1)
            # 存Log
            models_utils.save_recog_log(
                filename=filename,
                date_str=relative_path,          
                recog_model_id=model1.id,
                model_type=1,
                ip_address=ip_address,
                recog_image_name="",
                recog_content=result
            )

            # YOLO 偵測
            # 取食材模型
            model2 = models_utils.get_enabled_model(2)
           
            if model2 == None:
                return render(request, 'pages/test2.html',{"result":"請先上傳圖片"})
            else: 
                
                predictions, path = yolo.detect_image(filename, original_path, model2.model_path.path)

                # 查詢營養資訊 + 主分類中文
                food_infos, food_zh = yolo.query_food_infos(result, predictions)

                summary = yolo.sum_nutrition(food_infos)

                # ✅ 移除主分類，只保留 is_main=False 的項目（食材）
                food_infos = [info for info in food_infos if not info.get("is_main")]
                
                # 存Log        
                models_utils.save_recog_log(
                    filename=filename,
                    date_str=relative_path,
                    recog_model_id=model2.id,
                    model_type=2,
                    ip_address=ip_address,
                    recog_image_name=path,
                    recog_content=predictions
                )


                image_url = f"/original/{filename}"
                return render(request, 'pages/test2.html', {
                    'result': result,           # 英文主分類
                    'food_zh': food_zh,         # 中文主分類
                    'food_infos': food_infos,   # 食材 + 主分類列表
                    'summary': summary,         # 總營養
                    'image_url': image_src      # 傳給前端顯示圖片
                })
    # except Exception as e:
        # return render(request, 'pages/test2.html',{"result":"請先上傳圖片"})
       
        
        

