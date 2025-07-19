import os
from PIL import Image
from ultralytics import YOLO
from food_recognition.models import FoodNutrition 
from django.conf import settings
from datetime import datetime

def detect_image(image_input, save_dir: str = "outputs"):
    """
    使用 YOLO 模型進行圖片偵測，支援傳入檔案路徑或 PIL.Image，回傳結果圖路徑與辨識內容。

    參數:
        image_input (str | PIL.Image): 圖片檔案路徑或 PIL.Image 物件
        save_dir (str): 儲存偵測後圖片資料夾

    回傳:
        result_img_path (str): 儲存的圖片完整路徑
        predictions (list[dict]): 辨識結果
    """
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    save_dir = os.path.join(settings.BASE_DIR, save_dir, date_str)
    os.makedirs(save_dir, exist_ok=True)
    yolo_model_path = os.path.join(settings.BASE_DIR, 'best.pt')
    model = YOLO(yolo_model_path)

    # 判斷圖片輸入形式：字串路徑 or PIL.Image
    if isinstance(image_input, str):
        # 圖片來源為檔案路徑
        image_path = image_input
        save_name = os.path.basename(image_path)
    # elif isinstance(image_input, Image.Image):
    #     # 圖片來源為 PIL Image，先儲存為暫存檔
    #     image_path = os.path.join(save_dir, "temp_input.jpg")
    #     image_input.save(image_path)
    #     save_name = "temp_input.jpg"
    else:
        raise TypeError("image_input 必須是 str 或 PIL.Image")

    # 使用 model.predict 並指定儲存路徑
    results = model.predict(
        source=image_path,
        save=True,
        save_txt=False,      # 儲存 YOLO 格式的 推論標註文字檔
        project=save_dir,    # 用作根資料夾
        name="",             # 不加子資料夾
        exist_ok=True
    )

    # YOLO 自動儲存處理後圖檔於 save_dir/images
    result_img_path = os.path.join(save_dir, "project", save_name)

    # 辨識資訊整理
    boxes = results[0].boxes
    predictions = []
    for box in boxes:
        cls_id = int(box.cls[0])
        name = results[0].names[cls_id]
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        predictions.append({
            "name": name,
            "conf": round(conf, 4),
            "box": [round(coord, 1) for coord in xyxy]
        })

    return result_img_path, predictions

def query_food_infos(food, predictions):
    """
    回傳主分類食物與 YOLO 食材的營養資訊列表（含是否為主分類）。
    """
    seen = set()
    food_infos = []
    food_zh_name = food  # 預設主分類名稱就是英文（若查不到時用）

    # 加入主分類食物
    if food:
        try:
            main_food = FoodNutrition.objects.get(food_name_en__iexact=food)
            food_zh_name = main_food.food_name_zh  # 取中文名稱
            food_infos.append({
                "name_en": main_food.food_name_en,
                "name_zh": main_food.food_name_zh,
                "calories": main_food.calories,
                "protein": main_food.protein,
                "carbs": main_food.carbs,
                "is_main": True
            })
            seen.add(main_food.food_name_en.lower())
        except FoodNutrition.DoesNotExist:
            food_infos.append({
                "name_en": food,
                "error": "Not found in database",
                "is_main": True
            })
            seen.add(food.lower())

    # 加入 YOLO 偵測的食材
    for pred in predictions:
        name = pred['name']
        if name.lower() not in seen:
            seen.add(name.lower())
            try:
                ingredient = FoodNutrition.objects.get(food_name_en__iexact=name)
                food_infos.append({
                    "name_en": ingredient.food_name_en,
                    "name_zh": ingredient.food_name_zh,
                    "calories": ingredient.calories,
                    "protein": ingredient.protein,
                    "carbs": ingredient.carbs,
                    "is_main": False
                })
            except FoodNutrition.DoesNotExist:
                food_infos.append({
                    "name_en": name,
                    "error": "Not found in database",
                    "is_main": False
                })

    return food_infos, food_zh_name



def sum_nutrition(food_infos):
    """
    加總營養資訊：
    - 若有食材（非主分類，且有營養值），只加總食材。
    - 若無食材，則只加總主分類食物。
    """
    # 有任何非主分類且有熱量的食材
    ingredients = [i for i in food_infos if not i.get("is_main") and "calories" in i]

    if ingredients:
        items_to_sum = ingredients
        source = "食材"
    else:
        items_to_sum = [i for i in food_infos if i.get("is_main") and "calories" in i]
        source = "主分類"

    return {
        "total_calories": sum(i.get("calories", 0) for i in items_to_sum),
        "total_protein": sum(i.get("protein", 0) for i in items_to_sum),
        "total_carbs": sum(i.get("carbs", 0) for i in items_to_sum),
        "source": source,
        "item_count": len(items_to_sum)
    }

