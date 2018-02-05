from django.http  import Http404
from django.shortcuts import render,redirect
from . models import Image ,Profile, Like, Follow
import datetime as dt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from . forms import ImageForm, CommentForm, ProfileUpdateForm,UpdateImageCaption 
import os

@login_required(login_url='/accounts/login/')
def timeline(request):
    date = dt.date.today()
    timeline_images = Image.get_all_images()
    return render(request, 'all-grams/timeline.html',{"date":date,"timeline_images":timeline_images}) 

def search_results(request):
    if 'name' in request.GET and request.GET["name"]:
        search_name = request.GET.get("name")
        found_users = Profile.find_profile(search_name)
        message =f"{search_name}"

        return render(request,'all-grams/search_results.html',{"message":message,"found_users":found_users})
    else:
        message = "Please enter a valid username"
    return render(request,'all-grams/search_results.html',{"message":message})

def single_user(request,id):
    try:
        user = Profile.objects.get(id=id)
    except:
        raise Http404()
    return render(request,'all-grams/single.html',{"user":user,"user_images":user_images})

def single_image(request,image_id): 
    try:
        image = Image.objects.get(id= image_id)
    except:
        raise Http404()
    return render(request, 'all-grams/single_image.html',{"image":image})

@login_required(login_url='/accounts/login/')
def post(request):
    '''
    View function that displays a forms that allows users to upload images
    '''
    current_user = request.user

    if request.method == 'POST':

        form = ImageForm(request.POST ,request.FILES)

        if form.is_valid():
            image = form.save(commit = False)
            image.user_key = current_user
            image.likes +=1
            image.save() 

            return redirect( timeline)
    else:
        form = ImageForm() 
    return render(request, 'all-grams/post.html',{"form" : form}) 

def comment(request, image_id):
    current_image = Image.objects.get(id=image_id)
    current_user = request.user

    if request.method == 'POST':

        form = CommentForm(request.POST)
        logger_in = request.user

        if form.is_valid():
            comment = form.save(commit = False)
            comment.user_id= current_user
            comment.image_id = current_image

            comment.save() 
            return redirect(timeline)
    else:
        form = CommentForm()
    return render(request,'all-grams/comment.html',{"form":form})  

@login_required(login_url='/accounts/login/')
def update_profile(request):
    current_user = request.user 
    title = 'Update Profile'

    current_user = request.user
    requested_profile = Profile.objects.get(user_id = current_user.id)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST,request.FILES)

        if form.is_valid():
            requested_profile.profile_photo = form.cleaned_data['profile_photo']
            requested_profile.bio = form.cleaned_data['bio']
            requested_profile.username = form.cleaned_data['username']
            requested_profile.save_profile()
            return redirect( profile )
    else:
        form = ProfileUpdateForm()
    return render(request,'profile/update_profile.html',{"title":title,"current_user":current_user,"form":form})

def profile(request):
    title = 'Profile'
    current_user = request.user
    try:
        profile = Profile.objects.get(user_id = current_user)
        following = Follow.objects.filter(follower = current_user)
        followers = Follow.objects.filter(user = profile)
    except:
        raise Http404()

    return render(request, 'profile/profile.html',{"profile":profile,"current_user":current_user,"following":following,"followers":followers})

def more(request,image_id):
    image = Image.objects.get(id = image_id)

    current_user = request.user
    update_image = Image.objects.get(id= image_id)

    if request.method == 'POST':
        form = UpdateImageCaption(request.POST)
        if form.is_valid():
            new_caption = form.cleaned_data['image_caption']
            update_image.image_caption = new_caption
            update_image.save_image() 

            return redirect( more ,image_id)
    else:
        form = UpdateImageCaption()

    return render(request,'all-grams/more.html',{"image":image, "form":form}) 

def test(request):
    current_user = request.user
    following = Follow.objects.filter(user)

    

    return render(request, 'all-grams/test.html')

def view_profiles(request):
    all_profiles = Profile.objects.all()
    return render(request,'profile/all.html',{"all_profiles":all_profiles}) 

def follow(request,profile_id):
    current_user = request.user
    requested_profile = Profile.objects.get(id = profile_id)
    follower = Follow(follower = current_user,user = requested_profile)
    follower.save_follower() 
    return render(request,'profile/all.html') 

def like(request,image_id):
    requested_image = Image.objects.get(id = image_id)
    current_user = request.user
    
    if Like.objects.filter(image = requested_image).get(user = current_user ):
        requested_image.likes -1
        requested_image.save_image()
    else:
        requested_image.likes +=1
        requested_image.save_image()
    
    return render(request,'all-grams/timeline.html')






