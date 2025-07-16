from django.db import models
import os


class FoodNutrition(models.Model):
    food_name_en = models.CharField("食物名稱_英", max_length=50)
    food_name_zh = models.CharField("食物名稱_中", max_length=50)
    calories = models.DecimalField("熱量 (kcal)", max_digits=5, decimal_places=2)
    protein = models.DecimalField("蛋白質 (g)", max_digits=5, decimal_places=2)
    carbs = models.DecimalField("碳水化合物 (g)", max_digits=5, decimal_places=2)
    is_recog = models.BooleanField("是否可辨識", default=True)
    create_user = models.CharField("建立者", max_length=20)
    create_date = models.DateTimeField("建立時間", auto_now_add=True)
    update_user = models.CharField("更新者", max_length=20)
    update_date = models.DateTimeField("更新時間", auto_now=True)        

    class Meta:
        db_table = 'food_nutrition'

    def __str__(self):
        return f"{self.food_name_zh} / {self.food_name_en}"


class RecogLog(models.Model):
    image_name = models.CharField("圖檔名稱", max_length=50)
    image_path = models.CharField("圖檔路徑", max_length=50)
    recog_image_name = models.CharField("辨識圖檔名稱", max_length=50, null=True, blank=True)
    recog_content = models.CharField("辨識內容", max_length=200, null=True, blank=True)
    recog_model_id = models.IntegerField("模型ID")
    model_type = models.IntegerField("辨識類別")  # 1=菜餚, 2=食品
    create_ip = models.CharField("建立者IP", max_length=20)
    create_date = models.DateTimeField("建立時間")

    class Meta:
        db_table = 'food_recog_log'

    def __str__(self):
        return self.image_name

def model_upload_path(instance, filename):
    # 上傳到：models/2025_07/模型檔案.pt
    return f"models/{instance.create_date.strftime('%Y_%m')}/{filename}"

class RecogModel(models.Model):
    model_name = models.CharField("模型名稱", max_length=50)
    model_type = models.IntegerField("辨識類別")  # 1=菜餚, 2=食品
    model_file = models.FileField("上傳模型檔案", upload_to=model_upload_path, blank=True, null=True)
    model_path = models.CharField("模型檔案路徑", max_length=100, blank=True)  # 儲存上傳後的實體路徑
    recog_items = models.TextField("可辨識項目", max_length=1000)
    is_enabled = models.BooleanField("是否啟用", default=False)
    memo = models.TextField("備註", max_length=1000, null=True, blank=True)
    create_user = models.CharField("建立者", max_length=20)
    create_date = models.DateTimeField("建立時間", auto_now_add=True)
    update_user = models.CharField("更新者", max_length=20)
    update_date = models.DateTimeField("更新時間", auto_now=True)

    class Meta:
        db_table = 'food_recognition_recog_model'

    def __str__(self):
        return self.model_name
