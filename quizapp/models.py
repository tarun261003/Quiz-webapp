from django.db import models

# Create your models here.
class ExamControl(models.Model):
    exam_started = models.BooleanField(default=False)

    def __str__(self):
        return "Exam Started" if self.exam_started else "Exam Not Started"
from django.db import models
import markdown
from django.db import models
from django.contrib.auth.models import User
import time

class UserQuizProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    quiz_start_time = models.IntegerField(null=True, blank=True)  # Store timestamp
    quiz_duration = models.IntegerField(default=20 * 60)  # Default 20 minutes

class Question(models.Model):
    qno = models.IntegerField()
    question = models.TextField()  # Changed to TextField for better formatting
    o1 = models.CharField(max_length=100)
    o2 = models.CharField(max_length=100)
    o3 = models.CharField(max_length=100)
    o4 = models.CharField(max_length=100)
    co = models.CharField(max_length=100)

    def formatted_question(self):
        return markdown.markdown(self.question)  # Converts Markdown to HTML

    def __str__(self):
        return self.question



class fraud_model(models.Model):
    username = models.CharField(max_length=100)
    fraud = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username    
 
    


class leaderboard(models.Model):
    username = models.CharField(max_length=100)
    score = models.IntegerField()
    
    def __str__(self):
        return self.username    
 
    
