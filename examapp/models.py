# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Skills(models.Model):
    skill = models.CharField(max_length=255)

    def __str__(self):
        return self.skill
    
class Exam(models.Model):
    title = models.ForeignKey(Skills,on_delete=models.CASCADE)
    description = models.TextField(null=True)

    def __str__(self):
        return self.title.skill

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_title = models.CharField(max_length=200)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    answer = models.IntegerField()
    answer_defination = models.CharField(max_length=200) 

    def __str__(self):
        return self.question_title

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - {self.question.question_title}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

class UserExam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField(default=0,null=True,blank=True)
    attempts = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title.skill}"
    
class YouTubeVideo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

class WatchedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(YouTubeVideo, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now_add=True)
    
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)



class RoadMapList(models.Model):
    roadmap_name = models.CharField(max_length=255)
    skill = models.ManyToManyField(Skills)
    def __str__(self):
        return str(self.roadmap_name)

class RoadMap(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    roadmap = models.ForeignKey(RoadMapList,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return str(self.roadmap)
    
class FavouriteExam(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)    
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE)