from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from .models import Users
from django.contrib import messages
from django.contrib.auth.models import auth, User
# Create your views here.

def home(request):
    return render(request,'home.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['user-name']
        password = request.POST['password']
        
        user = auth.authenticate(username= username, password= password)
    
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Wrong Username or Password')
            return redirect('login')

    else:   
        return render(request,'login.html')

def signup(request):

    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        username = request.POST['user-name']
        email = request.POST['email']
        pass1 = request.POST['password']
        pass2 = request.POST['passwordcd']

        if pass1 == pass2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('signup')
            elif len(username) > 16:
                messages.info(request,'Username must be under 16 characters')
                return redirect('signup')
            elif not username.isalnum():
                messages.info(request,'Username must be alphanumeric')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, password=pass1, email=email, first_name=fname, last_name=lname)
                user.save()
                print('user created')
                return redirect('login')

        else:
            messages.info(request, 'Password not matching')
            return redirect('signup')

    else:
        return render(request,'signup.html')

def logout(request):
    auth.logout(request)
    return redirect('/')