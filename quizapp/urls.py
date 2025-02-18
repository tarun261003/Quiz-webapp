from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('',views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('fraud/', views.fraud, name='fraud'),
    path('report_fraud/', views.report_fraud, name='report_fraud'),
    path('exam_completed/',views.exam_completed,name='examcompleted'),
]