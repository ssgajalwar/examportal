# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Exam, Question, UserResponse, UserExam,YouTubeVideo,WatchedVideo,OTP,Profile,RoadMap,RoadMapList,Skills,FavouriteExam
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.models import User
from .forms import ProfileForm,YouTubeVideoForm,OTPForm, PasswordResetForm, SetPasswordForm
from django.http import HttpResponse
from django.db import models  # Ensure models import from Django
import json 
import requests
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
import pandas as pd
import os
import examapp
from . import roadmap_data
import math

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('roadmaps')
    else:
        form = UserCreationForm()
    return render(request, 'examapp/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('roadmaps')
        else:
            return render(request, 'examapp/login.html', {'error': 'Invalid username or password'})
    return render(request, 'examapp/login.html')

@login_required
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                otp = get_random_string(6, allowed_chars='0123456789')
                OTP.objects.create(user=user, otp=otp)
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP is {otp}',
                    'shreegajalwar@gmail.com',
                    [email],
                    fail_silently=False,
                )
                request.session['user_id'] = user.id
                return redirect('otp_verification')
    else:
        form = PasswordResetForm()
    return render(request, 'examapp/password_reset.html', {'form': form})

@login_required
def otp_verification(request):
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            user_id = request.session.get('user_id')
            user = User.objects.get(id=user_id)
            otp_record = OTP.objects.filter(user=user, otp=otp).first()
            if otp_record:
                request.session['verified_user_id'] = user.id
                return redirect('set_new_password')
    else:
        form = OTPForm()
    return render(request, 'examapp/otp_verification.html', {'form': form})

@login_required
def set_new_password(request):
    if request.method == 'POST' and request.user.is_authenticated:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update the session with the new password hash
            return redirect('login')  # Redirect to success page after password reset
    elif request.user.is_authenticated:
        form = PasswordChangeForm(request.user)
    else:
        return redirect('login')  # Redirect to login page if user is not authenticated

    return render(request, 'examapp/set_new_password.html', {'form': form})

@login_required
def home(request):
    if request.user:
        roadmap , create = RoadMap.objects.get_or_create(user=request.user)
        roadmap.save()
        recommended = []
        if roadmap.roadmap != None :  
            skillset =RoadMapList.objects.get(roadmap_name=roadmap)
            recommended = skillset.skill.all()

    if request.method == 'POST' and 'query' in request.POST:
        query = request.POST.get('query')
        exams = Exam.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        exams = Exam.objects.all()

    if request.user and request.method == 'POST' and 'favourite' in request.POST:
        favourite = request.POST.get('favourite')
        user = request.user
        exam = Exam.objects.get(id=favourite)
        favexam,create = FavouriteExam.objects.get_or_create(user=user,exam=exam)
    
        print("request received for adding in favourite",favourite)

    favourite_exams = FavouriteExam.objects.filter(user=request.user).select_related('exam')
    favourite_exams = [fav_exam.exam for fav_exam in favourite_exams]   


    return render(request, 'examapp/home.html', {
        'exams': exams,
        "roadmap":roadmap,
        "recommended_exams":recommended,
        "favourite_exams":favourite_exams
        })

@login_required
def exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = exam.question_set.all()[:25]
    if not questions:
        return HttpResponse("<h2>No Question Added Yet <a href='/'>Back to Home</a></h2>")
    return render(request, 'examapp/exam.html', {
        'questions': questions,
        'examname': exam,
        'exam_id': exam_id,
        'iterator': questions.__len__
    })

@login_required
def result(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    submitted_answers = request.POST
    total_questions = 0
    correct_answers = 0
    questions = Question.objects.filter(exam_id=exam_id).values('id', 'answer')
    for question in questions:
        question_id = "choice-" + str(question['id'])
        correct_answer = question['answer']
        if question_id in submitted_answers:
            submitted_answer = submitted_answers[question_id]
            if str(correct_answer) == submitted_answer:
                correct_answers += 1
        total_questions += 1
    score = correct_answers * 4 
      
    # Update or create UserExam record
    user_exam, created = UserExam.objects.get_or_create(user=request.user, exam=exam)
    print(user_exam)
    if not created:
        print(user_exam)
        user_exam.attempts += 1
        if score > user_exam.score:
            user_exam.score = score   
        user_exam.save()  
    else:
        user_exam.score = score   
        user_exam.save()   


    context = {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'exam': exam,
        'score': score,
    }
    return render(request, 'examapp/result.html', context)

@login_required
def dashboard(request):
    exams = UserExam.objects.filter(user=request.user)
    watched_videos = WatchedVideo.objects.filter(user=request.user)
    # Example: Fetching data for charts
    exam_titles = [exam.exam.title.skill for exam in exams]
    exam_scores = [exam.score or 0 for exam in exams]

    # Prepare data for ApexCharts
    chart_data = {
        'exam_titles': exam_titles,
        'exam_scores': exam_scores,
    }

    tup = []
    ranking = UserExam.objects.values_list('user',flat=True)
    for r in ranking:
        if tup.__contains__(r) :
            continue
        else:
            tup.append(r)

    
    return render(request, 'examapp/dashboard.html', {
        'watched_videos':watched_videos,
        'chart_data': json.dumps(chart_data),  # Convert Python dict to JSON string
    })

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    roadmap = RoadMap.objects.get(user=user)
    skill = []
    if roadmap.roadmap != None:
        skillset = RoadMapList.objects.get(roadmap_name = roadmap.roadmap)
        skill = skillset.skill.all()

    user_exams = UserExam.objects.filter(user=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user.profile)
    return render(request, 'examapp/profile.html', {
        'form': form,
        'user_exams': user_exams,
        "roadmap":roadmap.roadmap,
        "skillset": skill
    })

@login_required
def courses(request):
    videos = YouTubeVideo.objects.all()
    
    context = {
        'videos': videos,
        
    }
    return render(request, 'examapp/courses.html', context)

@login_required
def add_video(request):
    if request.method == 'POST':
        form = YouTubeVideoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = YouTubeVideoForm()
    return render(request, 'examapp/add_video.html', {'form': form})

@login_required
def mark_as_watched(request, video_id):
    video = YouTubeVideo.objects.get(id=video_id)
    WatchedVideo.objects.get_or_create(user=request.user, video=video)
    return redirect('courses')

@login_required
def tech_news(request):
    url = "https://newsapi.org/v2/everything?q=tesla&from=2024-06-08&sortBy=publishedAt&apiKey=cd421bb2a3ee4a52b7f145b55b2bcf4a"
    # params = {
    #     "category": "technology",
    #     "language": "en",
    #     "apiKey": settings.NEWS_API_KEY  # Ensure you have your API key in settings
    # }

    
    response = requests.get(url,timeout=5)
    news_data = response.json().get('articles', []) if response.status_code == 200 else []

    context = {
        'news_data': news_data
    }
    return render(request, 'examapp/tech_news.html', context)

@login_required
def settings(request):
    return render(request,'examapp/settings.html')

@login_required
def roadmaps(request):
    user = request.user
    roadmap_name = request.POST.get("roadmap")
    if request.method == "POST":
        rmprofile = RoadMapList.objects.get(roadmap_name=roadmap_name)
        exist_roadmap = RoadMap.objects.get(user=request.user)
        if exist_roadmap:
            exist_roadmap.roadmap=rmprofile
            exist_roadmap.save()
        else :
            roadmap , create = RoadMap.objects.get_or_create(user=request.user, roadmap=rmprofile)
            roadmap.save()

    
    roadmapsdb = RoadMapList.objects.all()
    context = {
        'roadmapdb':roadmapsdb
    }
    return render(request, 'examapp/roadmaps.html', context)

@login_required
def roadmap_detail(request, profile):
    profile_skills = RoadMapList.objects.get(roadmap_name=profile)
    context = {
        'profile': profile,
        'skills': profile_skills.skill.all()
    }
    return render(request, 'examapp/roadmap_details.html', context)


def loaddata(request):
    csv_filepath = os.path.abspath(examapp.__path__[0])+'\q_css.csv'
    csv_data = pd.read_csv(csv_filepath)
    # print(os.path.abspath(examapp.__path__[0]),"hello")
    # print(csv_filepath,"hello",csv_data)
    # print(type(csv_data))
    for index,row in csv_data.iterrows():
        subject = row["Subject"]
        sk = Skills.objects.get(skill=subject)
        exam = Exam.objects.get(title=sk)
        correct_option = float(row["correct_option"]) 
        if math.isnan(correct_option):
            correct_option = 0   
        
          
        question , create = Question.objects.get_or_create(
            exam=exam,
            question_title=row["Question"],
            option1=row["Option A"],
            option2=row["Option B"],
            option3=row["Option C"],
            option4=row["Option D"],
            answer= correct_option,  
            answer_defination=row["answerdef"]
        )  
        # question.save()
        # break
    return HttpResponse("Loading the Data....")

def loadroadmap(request):
    for roadmap_name, skills in roadmap_data.rdata.items():
    # Create or get the RoadMapList instance
        roadmap, created = RoadMapList.objects.get_or_create(roadmap_name=roadmap_name.capitalize())
    
        for skill_name in skills:
            # Create or get the Skill instance
            skill, created = Skills.objects.get_or_create(skill=skill_name)
            # Add the skill to the roadmap
            roadmap.skill.add(skill)
    
    return HttpResponse("Loading the Data....")


def loadexam(request):
    sk = Skills.objects.all()
    for s in sk:
        exam,create = Exam.objects.get_or_create(title=s,description="description")
        exam.save()
        print("saved",s)
    return HttpResponse("Loading Exams")      
