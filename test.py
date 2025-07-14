from modules.aimodels.cnn import classifyFood
from PIL import Image

# 讀取圖片
img = Image.open("beef.jpg")

# 顯示圖片（可選）
print(classifyFood(img))