from django.shortcuts import render

# Create your views here.
import joblib
import numpy as np
from django.http import JsonResponse


import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'model', 'accident_severity_model.pkl')
model = joblib.load(model_path)
label_model_path = os.path.join(BASE_DIR, 'model', 'label_encoders.pkl')
label_encoders = joblib.load(label_model_path)


def predict_safety(request):
    if request.method == 'POST':
        data = request.POST
        speed = float(data.get('speed'))
        vehicles = int(data.get('vehicles'))
        casualties = int(data.get('casualties'))
        day = int(data.get('day'))
        light = int(data.get('light'))
        weather = int(data.get('weather'))
        surface = int(data.get('surface'))
        urban = int(data.get('urban'))

        X = np.array([[speed, vehicles, casualties, day, light, weather, surface, urban]])
        prediction = model.predict(X)[0]

        return JsonResponse({'prediction': int(prediction)})
    return JsonResponse({'error': 'Invalid request'}, status=400)


from django.shortcuts import render

def index(request):
    return render(request, 'monitor/index.html')
