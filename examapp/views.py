# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Exam, Question, UserResponse, UserExam,YouTubeVideo,WatchedVideo,OTP,Profile
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

def home(request):
    if request.method == 'POST' and 'query' in request.POST:
        query = request.POST.get('query')
        exams = Exam.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        exams = Exam.objects.all()
    
    return render(request, 'examapp/home.html', {'exams': exams})

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
    score = correct_answers * 4 - (total_questions - correct_answers)
    
    # Update or create UserExam record
    user_exam, created = UserExam.objects.get_or_create(user=request.user, exam=exam)
    if not created:
        user_exam.attempts += 1
    user_exam.score = score
    user_exam.save()

    context = {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'exam': exam,
        'score': score,
    }
    return render(request, 'examapp/result.html', context)


def dashboard(request):
    exams = Exam.objects.all()
    watched_videos = WatchedVideo.objects.filter(user=request.user)
    # Example: Fetching data for charts
    exam_titles = [exam.title for exam in exams]
    exam_scores = [exam.userexam_set.aggregate(models.Sum('score'))['score__sum'] or 0 for exam in exams]

    # Prepare data for ApexCharts
    chart_data = {
        'exam_titles': exam_titles,
        'exam_scores': exam_scores,
    }

    return render(request, 'examapp/dashboard.html', {
        'watched_videos':watched_videos,
        'chart_data': json.dumps(chart_data),  # Convert Python dict to JSON string
    })



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
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
            return redirect('home')
        else:
            return render(request, 'examapp/login.html', {'error': 'Invalid username or password'})
    return render(request, 'examapp/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user = request.user
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
        'user_exams': user_exams
    })


# def courses(request):
#     url = "https://learn-online.p.rapidapi.com/Install_Header"

#     querystring = {"NEW_GET": "Install_Header"}

#     headers = {
#         "x-rapidapi-key": "9ca6668288msh216ee79442c9217p1c18f5jsndc64c33017c0",  # Replace with your actual API key
#         "x-rapidapi-host": "learn-online.p.rapidapi.com",
#         "NEW_Get": "Install_Header"
#     }

    # try:
    #     response = requests.get(url, headers=headers, params=querystring)
    #     response.raise_for_status()  # Raise an error for bad status codes
    #     data = response.json()  # Parse the JSON response
    # except requests.exceptions.RequestException as e:
    #     return HttpResponse(f"An error occurred: {e}")
    # except ValueError:
    #     return HttpResponse(f"Invalid JSON response: {response.text}")

    # Print the data for debugging purposes
    # print(data)

    # context = {
    #     'courses': ""
    # }

    # return render(request, 'examapp/courses.html', context)


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




def tech_news(request):
    url = "https://newsapi.org/v2/everything?q=tesla&from=2024-06-08&sortBy=publishedAt&apiKey=cd421bb2a3ee4a52b7f145b55b2bcf4a"
    # params = {
    #     "category": "technology",
    #     "language": "en",
    #     "apiKey": settings.NEWS_API_KEY  # Ensure you have your API key in settings
    # }

    
    response = requests.get(url)
    news_data = response.json().get('articles', []) if response.status_code == 200 else []
    # print(news_data,"hiii")
    context = {
        'news_data': news_data
    }
    return render(request, 'examapp/tech_news.html', context)


def settings(request):
    return render(request,'examapp/settings.html')

def roadmaps(request):
    roadmaps = {
        "Frontend": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue", "TypeScript", "Bootstrap", "Responsive Design", "GraphQL"],
        "Backend": ["Node.js", "Python", "Java", "C#", "PHP", "Ruby on Rails", "Spring Boot", "ASP.NET Core", "Go", "Django", "Flask", "SQL", "NoSQL", "RESTful APIs"],
        "DevOps": ["Linux", "Docker", "Kubernetes", "Terraform", "CI/CD", "Jenkins", "AWS", "Azure", "Google Cloud", "Ansible", "Prometheus", "Grafana"],
        "Full Stack": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Express.js", "MongoDB", "PostgreSQL", "Django", "Flask", "TypeScript", "GraphQL"],
        "AI and Data Scientist": ["Python", "R", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Data Visualization", "Machine Learning", "Deep Learning", "Statistics", "SQL"],
        "Data Analyst": ["Python", "R", "Excel", "SQL", "Tableau", "Power BI", "Data Cleaning", "Data Visualization", "Statistics", "Pandas", "NumPy"],
        "Android": ["Java", "Kotlin", "Android SDK", "Android Studio", "Gradle", "SQLite", "Firebase", "APIs", "XML"],
        "iOS": ["Swift", "Objective-C", "Xcode", "Cocoa Touch", "SQLite", "Firebase", "APIs", "Core Data", "SwiftUI"],
        "PostgreSQL": ["SQL", "PL/pgSQL", "Database Design", "Performance Tuning", "Backup and Recovery", "Security", "Data Modeling"],
        "Blockchain": ["Solidity", "Ethereum", "Smart Contracts", "Cryptography", "Bitcoin", "Hyperledger", "Consensus Algorithms", "DApps"],
        "QA": ["Manual Testing", "Automated Testing", "Selenium", "JUnit", "TestNG", "Performance Testing", "Load Testing", "Bug Tracking", "CI/CD"],
        "Software Architect": ["System Design", "Design Patterns", "Microservices", "Cloud Architecture", "Scalability", "Security", "API Design", "DevOps"],
        "Cyber Security": ["Network Security", "Penetration Testing", "Ethical Hacking", "Cryptography", "Incident Response", "Security Policies", "Firewall Management"],
        "UX Design": ["User Research", "Wireframing", "Prototyping", "Adobe XD", "Sketch", "Figma", "Usability Testing", "Interaction Design"],
        "Game Developer": ["Unity", "Unreal Engine", "C#", "C++", "Game Design", "3D Modeling", "Animation", "AI for Games", "Graphics Programming"],
        "Technical Writer": ["Technical Writing", "Documentation Tools", "API Documentation", "Markdown", "Content Management", "Editing", "Research"],
        "MLOps": ["Machine Learning", "CI/CD", "Docker", "Kubernetes", "TensorFlow", "PyTorch", "Model Deployment", "Model Monitoring", "AWS", "Azure"],
        "Product Manager": ["Product Lifecycle", "Agile Methodology", "Scrum", "Market Research", "Roadmapping", "Stakeholder Management", "User Stories"],
        "Developer Relations": ["Public Speaking", "Community Building", "Technical Writing", "Open Source Contribution", "Social Media", "Event Organization"],
        "Computer Science": ["Data Structures", "Algorithms", "Operating Systems", "Computer Networks", "Database Systems", "Theory of Computation"],
        "React": ["JavaScript", "JSX", "React Hooks", "Redux", "Context API", "React Router", "Testing Library", "TypeScript"],
        "Angular": ["TypeScript", "Components", "Services", "RxJS", "Angular CLI", "Forms", "Routing", "Testing"],
        "Vue": ["JavaScript", "Vue CLI", "Components", "Vuex", "Vue Router", "Composition API", "Directives", "Testing"],
        "JavaScript": ["ES6+", "DOM Manipulation", "Event Handling", "Asynchronous Programming", "Fetch API", "Web APIs", "JavaScript Frameworks"],
        "Node.js": ["JavaScript", "Express.js", "Asynchronous Programming", "RESTful APIs", "Database Integration", "Security", "Testing"],
        "TypeScript": ["JavaScript", "Static Typing", "Interfaces", "Classes", "Generics", "Modules", "Type Inference"],
        "Python": ["Syntax and Semantics", "Standard Library", "Web Frameworks", "Data Science Libraries", "Testing", "Automation"],
        "SQL": ["Queries", "Joins", "Indexes", "Stored Procedures", "Transactions", "Normalization", "Database Design"],
        "System Design": ["Scalability", "Load Balancing", "Caching", "Database Design", "Microservices", "API Design", "Security"],
        "API Design": ["RESTful APIs", "GraphQL", "Swagger/OpenAPI", "API Versioning", "Authentication", "Rate Limiting", "Documentation"],
        "ASP.NET Core": ["C#", ".NET Core", "MVC", "Entity Framework", "Razor Pages", "Web API", "Identity", "Testing"],
        "Java": ["OOP", "Java SE", "Java EE", "Spring Framework", "Hibernate", "JPA", "Concurrency", "Testing"],
        "C++": ["Syntax and Semantics", "STL", "OOP", "Memory Management", "Concurrency", "Templates", "C++11/14/17"],
        "Flutter": ["Dart", "Widgets", "State Management", "Flutter SDK", "Animations", "Plugins", "Testing"],
        "Spring Boot": ["Java", "Spring Framework", "Spring MVC", "Spring Data", "Spring Security", "Microservices", "Testing"],
        "Go": ["Syntax and Semantics", "Concurrency", "Standard Library", "Web Development", "Testing", "Deployment"],
        "Rust": ["Syntax and Semantics", "Ownership and Borrowing", "Concurrency", "Systems Programming", "WebAssembly"],
        "GraphQL": ["Schema Definition", "Queries and Mutations", "Resolvers", "Apollo Client", "Subscriptions", "Security"],
        "Design and Architecture": ["System Design", "Design Patterns", "Architectural Styles", "Scalability", "Security"],
        "Design System": ["UI Components", "Style Guides", "Theming", "Component Libraries", "Accessibility"],
        "React Native": ["JavaScript", "React", "Native Modules", "Navigation", "State Management", "Animations", "Testing"],
        "AWS": ["EC2", "S3", "RDS", "Lambda", "IAM", "CloudFormation", "DynamoDB", "VPC"],
        "Docker": ["Containers", "Dockerfile", "Docker Compose", "Image Management", "Networking", "Volumes"],
        "Kubernetes": ["Containers", "Pods", "Services", "Deployments", "ConfigMaps", "Secrets", "Helm"],
        "Linux": ["Shell Scripting", "System Administration", "Networking", "File Systems", "Security"],
        "MongoDB": ["NoSQL", "Document Model", "CRUD Operations", "Aggregation", "Indexing", "Replication"],
        "Prompt Engineering": ["AI Prompting", "Natural Language Processing", "Chatbot Development", "Conversational AI"],
        "Terraform": ["Infrastructure as Code", "Modules", "State Management", "Provisioning", "Providers"],
        "Data Structures & Algorithms": ["Arrays", "Linked Lists", "Trees", "Graphs", "Sorting", "Searching", "Dynamic Programming"],
        "Backend Performance": ["Caching", "Load Balancing", "Database Optimization", "Profiling", "Concurrency"],
        "Frontend Performance": ["Code Splitting", "Lazy Loading", "Compression", "Optimization Techniques"],
        "API Security": ["Authentication", "Authorization", "Rate Limiting", "Data Validation", "Encryption"]
    }
    
    context = {
        'roadmaps': roadmaps.keys()
    }
    return render(request, 'examapp/roadmaps.html', context)

def roadmap_detail(request, profile):
    roadmaps = {
        "Frontend": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue", "TypeScript", "Bootstrap", "Responsive Design", "GraphQL"],
        "Backend": ["Node.js", "Python", "Java", "C#", "PHP", "Ruby on Rails", "Spring Boot", "ASP.NET Core", "Go", "Django", "Flask", "SQL", "NoSQL", "RESTful APIs"],
        "DevOps": ["Linux", "Docker", "Kubernetes", "Terraform", "CI/CD", "Jenkins", "AWS", "Azure", "Google Cloud", "Ansible", "Prometheus", "Grafana"],
        "Full Stack": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Express.js", "MongoDB", "PostgreSQL", "Django", "Flask", "TypeScript", "GraphQL"],
        "AI and Data Scientist": ["Python", "R", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Data Visualization", "Machine Learning", "Deep Learning", "Statistics", "SQL"],
        "Data Analyst": ["Python", "R", "Excel", "SQL", "Tableau", "Power BI", "Data Cleaning", "Data Visualization", "Statistics", "Pandas", "NumPy"],
        "Android": ["Java", "Kotlin", "Android SDK", "Android Studio", "Gradle", "SQLite", "Firebase", "APIs", "XML"],
        "iOS": ["Swift", "Objective-C", "Xcode", "Cocoa Touch", "SQLite", "Firebase", "APIs", "Core Data", "SwiftUI"],
        "PostgreSQL": ["SQL", "PL/pgSQL", "Database Design", "Performance Tuning", "Backup and Recovery", "Security", "Data Modeling"],
        "Blockchain": ["Solidity", "Ethereum", "Smart Contracts", "Cryptography", "Bitcoin", "Hyperledger", "Consensus Algorithms", "DApps"],
        "QA": ["Manual Testing", "Automated Testing", "Selenium", "JUnit", "TestNG", "Performance Testing", "Load Testing", "Bug Tracking", "CI/CD"],
        "Software Architect": ["System Design", "Design Patterns", "Microservices", "Cloud Architecture", "Scalability", "Security", "API Design", "DevOps"],
        "Cyber Security": ["Network Security", "Penetration Testing", "Ethical Hacking", "Cryptography", "Incident Response", "Security Policies", "Firewall Management"],
        "UX Design": ["User Research", "Wireframing", "Prototyping", "Adobe XD", "Sketch", "Figma", "Usability Testing", "Interaction Design"],
        "Game Developer": ["Unity", "Unreal Engine", "C#", "C++", "Game Design", "3D Modeling", "Animation", "AI for Games", "Graphics Programming"],
        "Technical Writer": ["Technical Writing", "Documentation Tools", "API Documentation", "Markdown", "Content Management", "Editing", "Research"],
        "MLOps": ["Machine Learning", "CI/CD", "Docker", "Kubernetes", "TensorFlow", "PyTorch", "Model Deployment", "Model Monitoring", "AWS", "Azure"],
        "Product Manager": ["Product Lifecycle", "Agile Methodology", "Scrum", "Market Research", "Roadmapping", "Stakeholder Management", "User Stories"],
        "Developer Relations": ["Public Speaking", "Community Building", "Technical Writing", "Open Source Contribution", "Social Media", "Event Organization"],
        "Computer Science": ["Data Structures", "Algorithms", "Operating Systems", "Computer Networks", "Database Systems", "Theory of Computation"],
        "React": ["JavaScript", "JSX", "React Hooks", "Redux", "Context API", "React Router", "Testing Library", "TypeScript"],
        "Angular": ["TypeScript", "Components", "Services", "RxJS", "Angular CLI", "Forms", "Routing", "Testing"],
        "Vue": ["JavaScript", "Vue CLI", "Components", "Vuex", "Vue Router", "Composition API", "Directives", "Testing"],
        "JavaScript": ["ES6+", "DOM Manipulation", "Event Handling", "Asynchronous Programming", "Fetch API", "Web APIs", "JavaScript Frameworks"],
        "Node.js": ["JavaScript", "Express.js", "Asynchronous Programming", "RESTful APIs", "Database Integration", "Security", "Testing"],
        "TypeScript": ["JavaScript", "Static Typing", "Interfaces", "Classes", "Generics", "Modules", "Type Inference"],
        "Python": ["Syntax and Semantics", "Standard Library", "Web Frameworks", "Data Science Libraries", "Testing", "Automation"],
        "SQL": ["Queries", "Joins", "Indexes", "Stored Procedures", "Transactions", "Normalization", "Database Design"],
        "System Design": ["Scalability", "Load Balancing", "Caching", "Database Design", "Microservices", "API Design", "Security"],
        "API Design": ["RESTful APIs", "GraphQL", "Swagger/OpenAPI", "API Versioning", "Authentication", "Rate Limiting", "Documentation"],
        "ASP.NET Core": ["C#", ".NET Core", "MVC", "Entity Framework", "Razor Pages", "Web API", "Identity", "Testing"],
        "Java": ["OOP", "Java SE", "Java EE", "Spring Framework", "Hibernate", "JPA", "Concurrency", "Testing"],
        "C++": ["Syntax and Semantics", "STL", "OOP", "Memory Management", "Concurrency", "Templates", "C++11/14/17"],
        "Flutter": ["Dart", "Widgets", "State Management", "Flutter SDK", "Animations", "Plugins", "Testing"],
        "Spring Boot": ["Java", "Spring Framework", "Spring MVC", "Spring Data", "Spring Security", "Microservices", "Testing"],
        "Go": ["Syntax and Semantics", "Concurrency", "Standard Library", "Web Development", "Testing", "Deployment"],
        "Rust": ["Syntax and Semantics", "Ownership and Borrowing", "Concurrency", "Systems Programming", "WebAssembly"],
        "GraphQL": ["Schema Definition", "Queries and Mutations", "Resolvers", "Apollo Client", "Subscriptions", "Security"],
        "Design and Architecture": ["System Design", "Design Patterns", "Architectural Styles", "Scalability", "Security"],
        "Design System": ["UI Components", "Style Guides", "Theming", "Component Libraries", "Accessibility"],
        "React Native": ["JavaScript", "React", "Native Modules", "Navigation", "State Management", "Animations", "Testing"],
        "AWS": ["EC2", "S3", "RDS", "Lambda", "IAM", "CloudFormation", "DynamoDB", "VPC"],
        "Docker": ["Containers", "Dockerfile", "Docker Compose", "Image Management", "Networking", "Volumes"],
        "Kubernetes": ["Containers", "Pods", "Services", "Deployments", "ConfigMaps", "Secrets", "Helm"],
        "Linux": ["Shell Scripting", "System Administration", "Networking", "File Systems", "Security"],
        "MongoDB": ["NoSQL", "Document Model", "CRUD Operations", "Aggregation", "Indexing", "Replication"],
        "Prompt Engineering": ["AI Prompting", "Natural Language Processing", "Chatbot Development", "Conversational AI"],
        "Terraform": ["Infrastructure as Code", "Modules", "State Management", "Provisioning", "Providers"],
        "Data Structures & Algorithms": ["Arrays", "Linked Lists", "Trees", "Graphs", "Sorting", "Searching", "Dynamic Programming"],
        "Backend Performance": ["Caching", "Load Balancing", "Database Optimization", "Profiling", "Concurrency"],
        "Frontend Performance": ["Code Splitting", "Lazy Loading", "Compression", "Optimization Techniques"],
        "API Security": ["Authentication", "Authorization", "Rate Limiting", "Data Validation", "Encryption"]
    }
    
    profile_skills = roadmaps.get(profile, [])
    
    context = {
        'profile': profile,
        'skills': profile_skills
    }
    return render(request, 'examapp/roadmap_details.html', context)
