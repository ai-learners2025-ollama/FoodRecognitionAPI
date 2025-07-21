import os
from PIL import Image
from ultralytics import YOLO
from food_recognition.models import FoodNutrition 
from django.conf import settings
from datetime import datetime

def detect_image(image_input, save_dir: str = "models/"):
    """
    使用 YOLO 模型進行圖片偵測，支援傳入圖片路徑或 PIL.Image，回傳結果圖的相對路徑與辨識內容。
    """
    # 設定實體儲存路徑
    date_str = datetime.now().strftime('%Y_%m')
    save_dir_abs = os.path.join(settings.MEDIA_ROOT, save_dir, date_str)  # e.g., /.../media/models/2025_07
    os.makedirs(save_dir_abs, exist_ok=True)

    # 載入模型
    yolo_model_path = os.path.join(settings.BASE_DIR, 'best.pt')
    model = YOLO(yolo_model_path)

    # 處理輸入
    if isinstance(image_input, str):
        image_path = image_input
        save_name = os.path.basename(image_path)
    elif isinstance(image_input, Image.Image):
        save_name = "temp_input.jpg"
        image_path = os.path.join(save_dir_abs, save_name)
        
        # ext = os.path.splitext(image_path.name)[1]
        # uid = uuid.uuid4().hex
        # filename = f"{uid}{ext}"
        image_input.save(image_path)
    else:
        raise TypeError("image_input 必須是 str 或 PIL.Image")

    # 模型推論
    results = model.predict(
        source=image_path,
        save=True,
        save_txt=False,
        project=save_dir_abs,  # 真正存檔目錄
        name="",               # 不加子目錄
        exist_ok=True
    )

    # 結果圖片實際位置（預設 YOLO 存在 images 資料夾）
    result_img_abs_path = os.path.join(save_dir_abs, "images", save_name)

    # 將結果路徑轉為可用於前端的 MEDIA URL 相對路徑
    relative_path = os.path.relpath(result_img_abs_path, settings.MEDIA_ROOT)  # e.g., "models/2025_07/images/xxx.jpg"
    image_url = os.path.join(settings.MEDIA_URL, relative_path).replace("\\", "/")  # e.g., "/media/models/..."

    # 整理辨識結果
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

    return image_url, predictions

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

