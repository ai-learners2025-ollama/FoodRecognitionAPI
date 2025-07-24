import os
from PIL import Image
from ultralytics import YOLO
from food_recognition.models import FoodNutrition 
from django.conf import settings
from datetime import datetime

def detect_image(filename, original_path, model_file2):
    """
    使用 YOLO 模型進行圖片偵測，支援傳入圖片路徑或 PIL.Image，回傳結果圖的相對路徑與辨識內容。
    """
    try:
        # 設定實體儲存路徑
        date_str = datetime.now().strftime('%Y_%m')
        save_dir_abs = os.path.join(settings.MEDIA_IMAGE, date_str)  # e.g., /.../media/models/2025_07
        os.makedirs(save_dir_abs, exist_ok=True)

        # 載入模型（model_file2 為絕對路徑或相對於 BASE_DIR 的路徑）
        yolo_model_path = os.path.join(settings.BASE_DIR, model_file2)
        if not os.path.isfile(yolo_model_path):
            raise FileNotFoundError(f"模型檔案不存在：{yolo_model_path}")

        model = YOLO(yolo_model_path)

        # 模型推論
        results = model.predict(
            source=original_path,
            save=True,
            save_txt=False,
            project=save_dir_abs,
            name="",  # 不加子資料夾
            exist_ok=True
        )

        # 結果圖片儲存路徑        
        filename = f"{os.path.splitext(filename)[0]}.jpg"
        relative_path = os.path.join(settings.MEDIA_IMAGE_URL, date_str, 'predict', filename).replace('\\', '/')

        # 整理辨識結果
        boxes = results[0].boxes
        predictions = []
        for box in boxes:
            try:
                cls_id = int(box.cls[0])
                name = results[0].names[cls_id]
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                predictions.append({
                    "name": name,
                    "conf": round(conf, 4),
                    "box": [round(coord, 1) for coord in xyxy]
                })
            except Exception as box_err:
                print(f"[detect_image] 無法解析辨識框：{box_err}")

        return predictions, relative_path

    except Exception as e:
        print(f"[detect_image] 發生錯誤：{e}")
        return [], None

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
                "fat": main_food.fat,
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
                    "fat": ingredient.fat,
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
    try:
        # 有任何非主分類且有熱量的食材
        ingredients = [i for i in food_infos if not i.get("is_main") and "calories" in i]

        if ingredients:
            items_to_sum = ingredients
            source = "食材"
        else:
            items_to_sum = [i for i in food_infos if i.get("is_main") and "calories" in i]
            source = "主分類"

        return {
            "total_calories": sum(i.get("calories", 0) or 0 for i in items_to_sum),
            "total_protein": sum(i.get("protein", 0) or 0 for i in items_to_sum),
            "total_carbs": sum(i.get("carbs", 0) or 0 for i in items_to_sum),
            "total_fat": sum(i.get("fat", 0) or 0 for i in items_to_sum),
            "total_calories_pct": round((sum(i.get("calories", 0) or 0 for i in items_to_sum) / 2500) * 100),
            "total_protein_pct": round((sum(i.get("protein", 0) or 0 for i in items_to_sum) / 75) * 100),
            "total_carbs_pct": round((sum(i.get("carbs", 0) or 0 for i in items_to_sum) / 325) * 100),
            "total_fat_pct": round((sum(i.get("fat", 0) or 0 for i in items_to_sum) / 77) * 100),
            "source": source,
            "item_count": len(items_to_sum)
        }
    except Exception as e:
        print(f"[sum_nutrition] 錯誤：{e}")
        return {
            "total_calories": 0,
            "total_protein": 0,
            "total_carbs": 0,
            "total_fat": 0,
            "total_calories_pct": 0,
            "total_protein_pct": 0,
            "total_carbs_pct": 0,
            "total_fat_pct": 0,
            "source": "錯誤",
            "item_count": 0
        }


# | 項目           | 建議攝取量（每日）                    
# | ---------     | ---------------------------- 
# | **熱量**       | 男性：2500 kcal
# | **碳水化合物** |  325g（約每 1g 提供 4 kcal）   
# | **脂肪**       | 77g（約每 1g 提供 9 kcal）    
# | **蛋白質**     | 75g（約每 1g 提供 4 kcal）     
