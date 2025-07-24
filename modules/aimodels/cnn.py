from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np
import os
from django.conf import settings

img_size = 224
# classes = np.array(['beef_noodles', 'bubble_tea', 'curry_rice', 'donut', 'other', 'steak'])
# classes = np.array(['beef noodles', 'bubble_tea', 'curry_rice', 'donut', 'non_food', 'other_food', 'steak'])

classes = np.array([
    "beef noodles", "bubble_tea", "curry_rice", "donut",
    "non_food", "other_food_fried_rice", "other_food_hambuger",
    "other_food_noodle", "other_food_pizza",
    "other_food_stinky_tofu", "steak"
])

RabaClasses = np.array(['beef noodles', 'bubble_tea', 'curry_rice',
                        'donut', 'freid noodles', 'fried rice',
                        'hamburger', 'other', 'pizza', 'ramen',
                        'steak', 'stinky tofu'])

def classifyFood(food_img, model1):
    
    items = model1.recog_items
    classes = np.array([item.strip() for item in items.split(',')])

    # img = image.load_img(food_img, target_size=(img_size, img_size))
    img = food_img.resize((img_size, img_size)) 
    img = image.img_to_array(img) / 255.0
    img = np.expand_dims(img, axis = 0)

    model_path = os.path.join(settings.BASE_DIR, model1.model_path.path)
    model = load_model(model_path)

    pred = model.predict(img)

    result = classes[np.argmax(pred)]

    if result not in ['beef noodles', 'bubble_tea', 'curry_rice', 'donut', 'steak']:
        return "不在判別的五種食物中"
    
    return result

    '''
    confidence = np.max(pred)
    if confidence < 0.5:
        return f"模型不太確定這張圖片的內容，最高信心值為：{confidence:.2f}"
    else:
        return f"預測為類別 {result}，信心值為：{confidence:.2f}"
    '''