from django.shortcuts import render
from PIL import Image
from modules.aimodels.cnn import classifyFood

def test(request):
    if request.method == 'GET':
        return render(request, 'pages/test.html')
    else: 
        img = Image.open(request.FILES.get('image'))
        result = classifyFood(img)
        return render(request, 'pages/test.html', {'result': result})
