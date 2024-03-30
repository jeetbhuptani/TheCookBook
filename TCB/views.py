from django.shortcuts import render, redirect,get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.http import HttpResponse, HttpResponseNotFound
from .models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, F

def home(request):
    if request.method == 'POST':
        rname = request.POST['recipe']
        category_id = request.POST['category']
        cuisine_id = request.POST['cuisine']
        veg = request.POST['veg']
        non = request.POST['non-veg']

        recipe = Recipe.objects.filter(recipe_name=rname).values()

        context = {
            'recipe' : recipe,
        }
        return render(request,'home.html',context)
    category = Category.objects.all()
    cuisine = Cuisine.objects.all()
    recipe = Recipe.objects.all()
    context={
        'category':category,
        'cuisine':cuisine,
        'recipe': recipe,
    }
    return render(request,'home.html',context)

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

@login_required(login_url='/login')
def logout(request):
    auth.logout(request)
    return redirect('/')

def aboutus(request):
    return render(request,"aboutus.html")

@login_required(login_url='/login')
def account(request):
    
    if request.method == 'POST':
        user = request.user
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email'] 
        if fname.isalpha():
            user.first_name = fname
        else:
            messages.info(request,'Invalid Name')
            return redirect('account')
        if lname.isalpha():
            user.last_name = lname
        else:
            messages.info(request,'Invalid Name')
            return redirect('account')
        if email != user.email and User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('account')
        user.email = email
        user.save()
        return redirect('account')
    else:
        user = request.user
        recipes = Recipe.objects.filter(user=user)

        context={
            'user': user,
            'recipe' : recipes,
        }
        return render(request,"account.html",context)

@login_required(login_url='/login')
def urecipe(request):
    if request.method == 'POST':
        recipe_name = request.POST['recipename']
        category_id = request.POST['category']
        cuisine_id = request.POST['cuisine']
        veg = request.POST['veg']
        ingredients = request.POST['ingredients']
        steps = request.POST['steps']
        cooktime = request.POST['cooktime']
        serving = request.POST['serving']
        recipeimage = request.FILES['recipeimage']

        category = Category.objects.get(pk=category_id)
        cuisine = Cuisine.objects.get(pk=cuisine_id)

        recipe = Recipe.objects.create(
            user = request.user,
            recipe_name = recipe_name,
            recipe_image = recipeimage,
            recipe_steps = steps,
            ingredients = ingredients,
            cooking_time = cooktime,
            serving = serving,
            cuisine = cuisine, 
            category = category,
            veg = veg
        )
        print(recipe)
        recipe.save()
        messages.success(request,'Recipe Added Successfully')
        return redirect(account)

    else:
        category = Category.objects.all()
        cuisine = Cuisine.objects.all()
        context={
            "category": category,
            "cuisine": cuisine,
        }
        return render(request,"urecipe.html",context)

@login_required(login_url='/login')
def vrecipe(request,recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    user = request.user
    comment = Comment.objects.filter(user=user,recipe=recipe).first()
    all_comments = Comment.objects.filter(recipe=recipe)
    paginator = Paginator(all_comments,3)
    page_number = request.GET.get('page')
    try:
        comments = paginator.page(page_number)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    context={
        'recipe' : recipe,
        'comment' : comment,
        'comments' : comments,
    }
    return render(request,"vrecipe.html",context)

@login_required(login_url='/login')
def comment(request, recipe_id):
    if request.method == 'POST':
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            return HttpResponseNotFound("Recipe not found")

        comment_text = request.POST.get('comment')
        rating = request.POST.get('rate')

        if recipe.user == request.user:
            messages.info(request, "Cannot comment or rate your own recipe")
            return redirect(request.path)

        if rating:
            update_rating(request, recipe_id, rating)

        if comment_text:
            comment = Comment.objects.create(
                user=request.user,
                recipe=recipe,
                comment=comment_text
            )
            print(comment)
            return redirect('vrecipe', recipe_id=recipe_id)

    # Handle GET request if necessary
    return HttpResponse("GET request received for comment view")

        


def update_rating(request, recipe_id, rating):
    user = request.user
    
    # Update or create a new rating object
    existing_rating = Userrating.objects.filter(user=user, recipe_id=recipe_id).first()
    if existing_rating:
        existing_rating.rating = rating
        existing_rating.save()
    else:
        Userrating.objects.create(user=user, recipe_id=recipe_id, rating=rating)
        count = Recipe.objects.filter(pk=recipe_id).count + 1
        Recipe.objects.filter(pk=recipe_id).update(count=count)

    # Calculate the new average rating for the recipe
    new_average = Userrating.objects.filter(recipe_id=recipe_id).aggregate(Avg('rating'))['rating__avg']

    # Update the recipe with the new average rating
    Recipe.objects.filter(pk=recipe_id).update(rating=new_average)

    return

