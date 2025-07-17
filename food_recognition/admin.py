from django.contrib import admin
from .models import FoodNutrition, RecogLog, RecogModel
from import_export.admin import ExportMixin, ImportMixin, ImportExportModelAdmin
from django.utils import timezone
from import_export import resources, fields


class FoodNutritionResource(resources.ModelResource):
    # 指定要匯入的欄位
    food_name_zh = fields.Field(attribute='food_name_zh', column_name='food_name_zh')
    food_name_en = fields.Field(attribute='food_name_en', column_name='food_name_en')
    calories = fields.Field(attribute='calories', column_name='calories')
    protein = fields.Field(attribute='protein', column_name='protein')
    carbs = fields.Field(attribute='carbs', column_name='carbs')

    class Meta:
        model = FoodNutrition
        import_id_fields = ('food_name_zh', 'food_name_en')  # 根據中英文名稱作為唯一鍵
        # fields = ('food_name_zh', 'food_name_en', 'calories', 'protein', 'carbs')  # 只匯入這些
        fields = ('food_name_zh', 'food_name_en', 'calories', 'protein', 'carbs', 'create_user', 'update_user', 'is_recog')
        skip_unchanged = True
        report_skipped = True

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super().__init__(*args, **kwargs)

    def before_import_row(self, row, row_number=None, **kwargs):
        user = None
        if 'request' in self.context:
            user = self.context['request'].user

        row['is_recog'] = True
        row['create_user'] = user.username if user else 'import_user'
        row['update_user'] = user.username if user else 'import_user'
        
        
@admin.register(FoodNutrition)
class FoodNutritionAdmin(ImportExportModelAdmin):
    resource_class = FoodNutritionResource
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
    
    def get_import_resource_kwargs(self, request, *args, **kwargs):
        return {'context': {'request': request}}


admin.site.register(RecogLog)

@admin.register(RecogModel)
class RecogModelAdmin(admin.ModelAdmin):
    readonly_fields = ('model_file','create_user', 'create_date', 'update_date', 'update_user')  # 管理頁面不可編輯

    # 新增頁面不顯示更新欄位（exclude 就是排除欄位）
    exclude = ('model_file','create_user', 'create_date', 'update_date', 'update_user')
    
    def save_model(self, request, obj, form, change):
        if obj.model_path:
            obj.model_file = obj.model_path.name 
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
        