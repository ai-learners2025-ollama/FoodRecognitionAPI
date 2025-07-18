import django
from modules.aimodels.cnn import classifyFood
from PIL import Image
from ultralytics import YOLO

# # 讀取圖片
# img = Image.open("beef.jpg")

# # 顯示圖片（可選）
# print(classifyFood(img))


# model = YOLO('C:/Users/user/Desktop/FoodRecognitionAPI/best.pt')  # 路徑換成你模型路徑
# results = model('C:/Users/user/Desktop/FoodRecognitionAPI/beef.jpg')

# print(results)  

from ultralytics import YOLO

model = YOLO('best.pt')
results = model('beef.jpg')
results[0].show() # 顯示偵測結果圖片

