from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np

img_size = 224
classes = np.array(['beef_noodles', 'braised_pork_rice', 'bubble_tea', 'curry_rice', 'steak'])

def classifyFood(food_img):
    # img = image.load_img(food_img, target_size=(img_size, img_size))
    img = food_img.resize((img_size, img_size)) 
    img = image.img_to_array(img) / 255.0
    img = np.expand_dims(img, axis = 0)

    model = load_model('food_model.keras')

    pred = model.predict(img)
    
    # print("預測結果：", classes[np.argmax(pred)])
    return classes[np.argmax(pred)]

# print(classifyFood('sss'))
