from django.contrib import admin
from .models import Exam, Question, Choice, UserResponse,YouTubeVideo,WatchedVideo

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(UserResponse)
admin.site.register(YouTubeVideo)
admin.site.register(WatchedVideo)
