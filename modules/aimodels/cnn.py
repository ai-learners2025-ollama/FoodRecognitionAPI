from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np
import os
from django.conf import settings

img_size = 224
classes = np.array(['beef_noodles', 'bubble_tea', 'curry_rice', 'donut', 'other', 'steak'])

def classifyFood(food_img):
    # img = image.load_img(food_img, target_size=(img_size, img_size))
    img = food_img.resize((img_size, img_size)) 
    img = image.img_to_array(img) / 255.0
    img = np.expand_dims(img, axis = 0)

    model_path = os.path.join(settings.BASE_DIR, 'food_model.keras')
    model = load_model(model_path)

    pred = model.predict(img)

    confidence = np.max(pred)
    predicted_class = np.argmax(pred)

    result = classes[np.argmax(pred)]

    if result == 'other':
        return "不在判別的五種食物中"
    else:
        return result

    # if confidence < 0.5:
    #     return f"模型不太確定這張圖片的內容，最高信心值為：{confidence:.2f}"
    # else:
    #     return f"預測為類別 {classes[predicted_class]}，信心值為：{confidence:.2f}"
    
    # print("預測結果：", classes[np.argmax(pred)])
    # return classes[np.argmax(pred)]

# print(classifyFood('sss'))
