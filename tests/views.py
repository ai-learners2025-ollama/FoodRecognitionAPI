from django.shortcuts import render
from PIL import Image
from modules.aimodels.cnn import classifyFood
from modules.aimodels.yolo import detect_image, query_unique_food_info

def test(request):
    if request.method == 'GET':
        return render(request, 'pages/test.html')
    else: 
        img = Image.open(request.FILES.get('image'))
         # 分類模型：主類別分類（如 牛肉麵 / 咖哩飯）
        result = classifyFood(img)

        # 物件偵測模型：辨識出多個食材位置與名稱
        path, predictions = detect_image(img)

        # 查詢營養資訊（排除重複）
        food_infos = query_unique_food_info(result, predictions)

        return render(request, 'pages/test.html', {
            'result': result,
            'food_infos': food_infos,
        })
