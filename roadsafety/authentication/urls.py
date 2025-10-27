from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('sensor-monitor/', views.sensor_monitor, name='sensor_monitor'),  # New page
    path('api/predict-behavior/', views.predict_behavior, name='predict_behavior'),  # API endpoint
]
