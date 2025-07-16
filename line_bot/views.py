from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from modules.aimodels.cnn import classifyFood
from PIL import Image
import io
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
                    image = Image.open(io.BytesIO(image_bytes))

                    result = classifyFood(image)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="你傳送的食物是: " + result)
                    )
                else:
                    pass
                    # print("文字以外的類型\n")
            else:
                pass
                # print("非訊息事件")

    return HttpResponse()
