from django.contrib import admin
from .models import FoodNutrition, RecogLog, RecogModel
from import_export.admin import ExportMixin, ImportMixin, ImportExportModelAdmin
from django.utils import timezone
from import_export import resources, fields
from django.conf import settings
import os
from django.utils.html import format_html


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
    # 清單頁
    list_display = ('food_name_en', 'food_name_zh', 'calories', 'protein', 'carbs', 'is_recog', 'create_user', 'create_date', 'update_user', 'update_date')
    search_fields = ('food_name_en', 'food_name_zh')   
    ordering = ('food_name_en',)  # 按照出版日期排序
    list_per_page = 50  # 每页显示 25 条记录
    
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


@admin.register(RecogLog)
class RecogLogAdmin(admin.ModelAdmin):
    # 清單頁
    list_display = ('image_name', 'model_type', 'recog_content', 'recog_model_id', 'create_ip', 'create_date')     
    ordering = ('create_date',)  # 按照出版日期排序
    list_per_page = 50  # 每页显示 25 条记录
    
       
    # 禁止新增功能
    def has_add_permission(self, request):
        return False

    # 禁止编辑功能
    def has_change_permission(self, request, obj=None):
        return False
    
    # 顯示圖片預覽
    def image_preview(self, obj):
        if obj.image_path:
           
            # 返回圖片的 HTML 標籤，並設置預覽尺寸
            return format_html('<img src="{0}" width="150" height="150" />', obj.image_path)
           
        return '無圖片'

    image_preview.allow_tags = True  # 允許返回 HTML 標籤
    image_preview.short_description = '圖片預覽'
       
    def recog_image_name_view(self, obj):
        if obj.recog_image_name:
           
            # 返回圖片的 HTML 標籤，並設置預覽尺寸
            return format_html('<img src="{0}" width="150" height="150" />', obj.recog_image_name)
           
        return '無圖片'

    recog_image_name_view.allow_tags = True  # 允許返回 HTML 標籤
    recog_image_name_view.short_description = '圖片預覽'

    # 在詳細頁面顯示圖片預覽
    readonly_fields = ('image_preview','recog_image_name_view')

     

@admin.register(RecogModel)
class RecogModelAdmin(admin.ModelAdmin):
    # 清單頁
    list_display = ('model_name', 'model_type', 'model_file', 'update_date')
    search_fields = ('model_name', 'model_type',)
    ordering = ('update_date',)  # 按照出版日期排序
    list_per_page = 50  # 每页显示 25 条记录
    
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
        