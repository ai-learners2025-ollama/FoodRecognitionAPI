from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from modules.aimodels import cnn, yolo
from utils import image_utils, models_utils

from PIL import Image
import io
import base64
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import StickerMessage, StickerSendMessage
from linebot.models import ImageMessage, ImageSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    if (request.method == "POST"):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')


        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden
        except LineBotApiError:
            return HttpResponseBadRequest()


        for event in events:
            # print("收到訊息", event, "\n")
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    # print("收到訊息:", event.message.text, "\n")
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請傳送食物照片!!!")
                    )
                elif isinstance(event.message, ImageMessage):
                    # print("收到圖片", event.message)
                    # image_name = event.message.id + ".jpg"
                    image_content = line_bot_api.get_message_content(event.message.id)

                    image_bytes = b"".join(chunk for chunk in image_content.iter_content())

                    img_src = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("utf-8")
                    # 取IP
                    ip_address = models_utils.get_client_ip(request)  # 你需要另外定義這個函式

                    # 儲存圖檔
                    # filename, original_path, relative_path = image_utils.uploaded_image(img_src)
                    filename, original_path, relative_path = image_utils.uploaded_base64_image(img_src)

                    img = Image.open(original_path)
                    img = img.convert('RGB')  #  RGB 格式

                    # 取食物模型
                    model1 = models_utils.get_enabled_model(1)

                    # 主分類（英文）
                    result = cnn.classifyFood(img, model1)

                    # 存Log
                    models_utils.save_recog_log(
                        filename=filename,
                        date_str=relative_path,          
                        recog_model_id=model1.id,
                        model_type=1,
                        ip_address=ip_address,
                        recog_image_name="",
                        recog_content=result
                    )


                    # YOLO 偵測
                    # 取食材模型
                    model2 = models_utils.get_enabled_model(2)
                
                    if model2 == None:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="系統維護中: ")
                        )
                    else: 
                        
                        predictions, path = yolo.detect_image(filename, original_path, model2.model_path.path)

                        # 查詢營養資訊 + 主分類中文
                        food_infos, food_zh = yolo.query_food_infos(result, predictions)

                        summary = yolo.sum_nutrition(food_infos)

                        # ✅ 移除主分類，只保留 is_main=False 的項目（食材）
                        food_infos = [info for info in food_infos if not info.get("is_main")]
                        
                        # 存Log        
                        models_utils.save_recog_log(
                            filename=filename,
                            date_str=relative_path,
                            recog_model_id=model2.id,
                            model_type=2,
                            ip_address=ip_address,
                            recog_image_name=path,
                            recog_content=predictions
                        )

                        food_inside = "".join([food.get('name_zh') or food.get('name_en') for food in food_infos]) + " "
                    
                        res_message = f"辨識食物: {food_zh} \n " + \
                                      f"食材: {food_inside} \n" + \
                                      f"熱量: {summary['total_calories']} \n" + \
                                      f"蛋白質: {summary['total_protein']} \n" + \
                                      f"碳水: {summary['total_carbs']} \n" + \
                                      f"脂肪: {summary['total_fat']}"

                        # 創建一個訊息列表
                        messages_to_send = []

                        # 添加文字訊息
                        messages_to_send.append(TextSendMessage(text=res_message))

                        # 生成圖片 URL
                        # 更健壯的協定判斷 (尤其在有反向代理的環境下)
                        # 優先檢查 X-Forwarded-Proto Header，如果沒有再 fallback 到 is_secure()
                        scheme = request.headers.get('X-Forwarded-Proto') or \
                                 ("https" if request.is_secure() else "http")
                        yolo_pred_img_url = f'{scheme}://{request.get_host()}{path}'
                        print(yolo_pred_img_url)
                        # 添加圖片訊息
                        messages_to_send.append(
                            ImageSendMessage(
                                preview_image_url=yolo_pred_img_url,
                                original_content_url=yolo_pred_img_url,
                            )
                        )

                        # 一次性回覆所有訊息
                        line_bot_api.reply_message(
                            event.reply_token,
                            messages_to_send  # 將訊息列表傳遞給 reply_message
                        )
                else:
                    pass
                    # print("文字以外的類型\n")
            else:
                pass
                # print("非訊息事件")

    return HttpResponse()
