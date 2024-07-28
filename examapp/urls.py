from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('exam/<int:exam_id>/', views.exam, name='exam'),
    # path('exam/<int:exam_id>/question/<int:question_id>/', views.question, name='question'),
    path('exam/<int:exam_id>/result/', views.result, name='result'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.courses, name='courses'),
    path('add_video/', views.add_video, name='add_video'),
    path('mark_as_watched/<int:video_id>/', views.mark_as_watched, name='mark_as_watched'),
    path('tech_news/', views.tech_news, name='tech_news'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
    path('settings/',views.settings,name='settings'),
    path('roadmaps/',views.roadmaps,name='roadmaps'),
    path('roadmaps/<str:profile>/', views.roadmap_detail, name='roadmap_detail'),

    # Load Data
    path('loaddata/',views.loaddata,name='loaddata'),
    path('loadroadmap/',views.loadroadmap,name='loadroadmap'),
    path('loadexam/',views.loadexam,name='loadexam'),

]
