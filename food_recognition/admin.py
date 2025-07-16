from django.contrib import admin
from .models import FoodNutrition, RecogLog, RecogModel
from import_export.admin import ExportMixin, ImportMixin, ImportExportModelAdmin
from django.utils import timezone

@admin.register(FoodNutrition)
class FoodNutritionAdmin(ImportExportModelAdmin):
    readonly_fields = ('create_user', 'create_date', 'update_date', 'update_user')  # 管理頁面不可編輯

    # 新增頁面不顯示更新欄位（exclude 就是排除欄位）
    exclude = ('create_user', 'create_date', 'update_date', 'update_user')
    
    def save_model(self, request, obj, form, change):
        if change:
            # 修改時自動更新
            obj.update_date = timezone.now()
            obj.update_user = request.user.username
        else:
            # 新增時帶入建立者與建立時間
            obj.create_date = timezone.now()
            obj.create_user = request.user.username
            obj.update_date = timezone.now()
            obj.update_user = request.user.username
        super().save_model(request, obj, form, change)


admin.site.register(RecogLog)

@admin.register(RecogModel)
class RecogModelAdmin(ImportExportModelAdmin):
    readonly_fields = ('model_path','create_user', 'create_date', 'update_date', 'update_user')  # 管理頁面不可編輯

    # 新增頁面不顯示更新欄位（exclude 就是排除欄位）
    exclude = ('model_path','create_user', 'create_date', 'update_date', 'update_user')
    
    def save_model(self, request, obj, form, change):
        if obj.model_file:
            obj.model_path = obj.model_file.name 
        if change:
            # 修改時自動更新
            obj.update_date = timezone.now()
            obj.update_user = request.user.username
        else:
            # 新增時帶入建立者與建立時間
            obj.create_date = timezone.now()
            obj.create_user = request.user.username
            obj.update_date = timezone.now()
            obj.update_user = request.user.username
        super().save_model(request, obj, form, change)
        