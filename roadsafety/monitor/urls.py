from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('predict/', views.predict_safety, name='predict'),
]
