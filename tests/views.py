from django.shortcuts import render
from PIL import Image
from modules.aimodels.cnn import classifyFood
from modules.aimodels.yolo import detect_image, query_food_infos, sum_nutrition

def test(request):
    if request.method == 'GET':
        return render(request, 'pages/test.html')
    else: 
        img = Image.open(request.FILES.get('image'))

        # 主分類（英文）
        result = classifyFood(img)

        # YOLO 偵測
        path, predictions = detect_image(img)

        # 查詢營養資訊 + 主分類中文
        food_infos, food_zh = query_food_infos(result, predictions)

        summary = sum_nutrition(food_infos)

         # ✅ 移除主分類，只保留 is_main=False 的項目（食材）
        food_infos = [info for info in food_infos if not info.get("is_main")]
        
        return render(request, 'pages/test.html', {
            'result': result,           # 英文主分類
            'food_zh': food_zh,         # 中文主分類
            'food_infos': food_infos,   # 食材 + 主分類列表
            'summary': summary,         # 總營養
        })
        
        

