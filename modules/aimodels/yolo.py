import os
from PIL import Image
from ultralytics import YOLO
from food_recognition.models import FoodNutrition 

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
    os.makedirs(save_dir, exist_ok=True)
    model = YOLO('best.pt')

    # 判斷圖片輸入形式：字串路徑 or PIL.Image
    if isinstance(image_input, str):
        image_path = image_input
        results = model(image_path, save=True, save_dir=save_dir)
        save_name = os.path.basename(image_path)
    elif isinstance(image_input, Image.Image):
        # 給予暫存檔名
        temp_path = os.path.join(save_dir, "temp_input.jpg")
        image_input.save(temp_path)
        results = model(temp_path, save=True, save_dir=save_dir)
        save_name = "temp_input.jpg"
    else:
        raise TypeError("image_input 必須是 str 或 PIL.Image")

    # YOLO 自動儲存處理後圖檔於 save_dir/images
    result_img_path = os.path.join(save_dir, "images", save_name)

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

def query_unique_food_info(food, predictions):
    """
    根據 YOLO 辨識結果查詢資料庫，將主分類食材優先放前，並去除重複。

    參數:
        food (str): 主分類模型預測結果（如 'Beef noodles'）
        predictions (list[dict]): YOLO 偵測結果，包含 'name'

    回傳:
        food_infos (list[dict]): 包含營養資訊與是否為主分類食材
    """
    seen = set()
    food_infos = []

    # 加入主分類食材（如果在資料庫中找得到）
    if food:
        try:
            main_food = FoodNutrition.objects.get(food_name_en__iexact=food)
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
                food = FoodNutrition.objects.get(food_name_en__iexact=name)
                food_infos.append({
                    "name_en": food.food_name_en,
                    "name_zh": food.food_name_zh,
                    "calories": food.calories,
                    "protein": food.protein,
                    "carbs": food.carbs,
                    "is_main": False
                })
            except FoodNutrition.DoesNotExist:
                food_infos.append({
                    "name_en": name,
                    "error": "Not found in database",
                    "is_main": False
                })

    return food_infos