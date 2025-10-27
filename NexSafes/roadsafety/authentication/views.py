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
