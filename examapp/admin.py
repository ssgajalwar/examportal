from django.contrib import admin
from .models import Exam, Question, Choice, UserResponse,YouTubeVideo,WatchedVideo,RoadMapList,RoadMap,Skills

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(UserResponse)
admin.site.register(YouTubeVideo)
admin.site.register(WatchedVideo)
admin.site.register(RoadMapList)
admin.site.register(RoadMap)
admin.site.register(Skills)
