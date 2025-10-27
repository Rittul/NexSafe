from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile

def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('/register/')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('/register/')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('/register/')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()
        
        # Create profile for the new user
        UserProfile.objects.create(user=user)
        
        messages.success(request, "Account created successfully! Please login.")
        return redirect('/login/')
    
    return render(request, 'authentication/register.html')

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login/')
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/home/')
    
    return render(request, 'authentication/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('/login/')

@login_required
def home(request):
    return render(request, 'authentication/home.html')

@login_required
def profile(request):
    # Get or create profile automatically
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update user details
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile details
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.pincode = request.POST.get('pincode', '')
        profile.bio = request.POST.get('bio', '')
        profile.date_of_birth = request.POST.get('date_of_birth', None)
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('/profile/')
    
    context = {
        'user': request.user,
        'profile': profile
    }
    return render(request, 'authentication/profile.html', context)



# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from .models import UserProfile
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# import json
# import joblib
# import numpy as np
# import os
# from pathlib import Path

# # Load ML model and scaler once when Django starts
# BASE_DIR = Path(__file__).resolve().parent.parent
# MODEL_PATH = BASE_DIR / 'model' / 'driver_behaviour.pkl'  # Changed ml_models to model
# SCALER_PATH = BASE_DIR / 'model' / 'scaler.pkl'  


# # print("=" * 60)
# # print("DEBUG INFO:")
# # print(f"Current file: {__file__}")
# # print(f"BASE_DIR: {BASE_DIR}")
# # print(f"MODEL_PATH: {MODEL_PATH}")
# # print(f"SCALER_PATH: {SCALER_PATH}")
# # print(f"Model file exists: {MODEL_PATH.exists()}")
# # print(f"Scaler file exists: {SCALER_PATH.exists()}")
# # model_dir = BASE_DIR / 'model'

# # Load model if files exist
# try:
#     with open(MODEL_PATH, 'rb') as f:
#         model = joblib.load(MODEL_PATH)
#     with open(SCALER_PATH, 'rb') as f:
#         scaler = joblib.load(SCALER_PATH)
#     MODEL_LOADED = True
# except FileNotFoundError:
#     MODEL_LOADED = False
#     print("⚠️ Warning: ML model files not found. Place them in ml_models/ folder.")
#     # print(f"\n❌ Model directory does not exist: {model_dir}")



# @csrf_exempt  # Remove this in production, use proper CSRF
# @require_http_methods(["POST"])
# def predict_behavior(request):
#     """
#     API endpoint to predict driver behavior from sensor data
#     """
#     if not MODEL_LOADED:
#         return JsonResponse({
#             'error': 'Model not loaded. Please upload model files.'
#         }, status=500)
    
#     try:
#         # Parse incoming JSON data
#         data = json.loads(request.body)
        
#         # Extract sensor values in correct order
#         # Order: accel_2, accel_3, accel_4, gyro_2, gyro_3, gyro_4, proximity
#         sensor_values = [
#             float(data.get('accel_2', 0)),
#             float(data.get('accel_3', 0)),
#             float(data.get('accel_4', 0)),
#             float(data.get('gyro_2', 0)),
#             float(data.get('gyro_3', 0)),
#             float(data.get('gyro_4', 0)),
#             float(data.get('proximity', 0))
#         ]
        
#         # Convert to numpy array
#         sensor_array = np.array([sensor_values])
        
#         # Scale the data
#         sensor_scaled = scaler.transform(sensor_array)
        
#         # Predict
#         prediction = model.predict(sensor_scaled)[0]
#         probability = model.predict_proba(sensor_scaled)[0]
        
#         # Return result
#         return JsonResponse({
#             'behavior': 'risky' if prediction == 1 else 'safe',
#             'confidence': float(probability[prediction] * 100),
#             'risky_probability': float(probability[1] * 100),
#             'safe_probability': float(probability[0] * 100)
#         })
        
#     except Exception as e:
#         return JsonResponse({
#             'error': str(e)
#         }, status=400)

# @login_required
# def sensor_monitor(request):
#     """
#     Page to monitor driver behavior using phone sensors
#     """
#     return render(request, 'authentication/sensor_monitor.html')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import joblib
import numpy as np
import pandas as pd  # ✅ Added for DataFrame
import os
from pathlib import Path


# Load ML model and scaler once when Django starts
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'model' / 'driver_behaviour.pkl'
SCALER_PATH = BASE_DIR / 'model' / 'scaler.pkl'

# Load model if files exist
try:
    # ✅ Fixed: Use joblib.load() directly, no need for 'with open'
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    MODEL_LOADED = True
    print("✅ ML MODEL LOADED SUCCESSFULLY!")
except FileNotFoundError:
    MODEL_LOADED = False
    print("⚠️ Warning: ML model files not found.")
except Exception as e:
    MODEL_LOADED = False
    print(f"⚠️ Error loading model: {e}")


@csrf_exempt  # Remove this in production, use proper CSRF
@require_http_methods(["POST"])
def predict_behavior(request):
    """
    API endpoint to predict driver behavior from sensor data
    """
    if not MODEL_LOADED:
        return JsonResponse({
            'error': 'Model not loaded. Please upload model files.'
        }, status=500)
    
    try:
        # Parse incoming JSON data
        data = json.loads(request.body)
        
        # ✅ Fixed: Create DataFrame with feature names (eliminates warning)
        sensor_data = pd.DataFrame([{
            'accel_2': float(data.get('accel_2', 0)),
            'accel_3': float(data.get('accel_3', 0)),
            'accel_4': float(data.get('accel_4', 0)),
            'gyro_2': float(data.get('gyro_2', 0)),
            'gyro_3': float(data.get('gyro_3', 0)),
            'gyro_4': float(data.get('gyro_4', 0)),
            'proximity': float(data.get('proximity', 0))
        }])
        
        # Scale the data (now with proper feature names)
        sensor_scaled = scaler.transform(sensor_data)
        
        # Predict
        prediction = model.predict(sensor_scaled)[0]
        probability = model.predict_proba(sensor_scaled)[0]
        
        # Return result
        return JsonResponse({
            'behavior': 'risky' if prediction == 1 else 'safe',
            'confidence': float(probability[prediction] * 100),
            'risky_probability': float(probability[1] * 100),
            'safe_probability': float(probability[0] * 100)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)


@login_required
def sensor_monitor(request):
    """
    Page to monitor driver behavior using phone sensors
    """
    return render(request, 'authentication/sensor_monitor.html')
