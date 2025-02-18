from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import random
from . import models

def user_login(request):
    """Handles user authentication and prevents fraud users from logging in."""
    context = {}

    if request.method == "POST":
        uname = request.POST.get('uname', '').strip().upper()
        password = request.POST.get('password', '').strip()

        # Check if the user is flagged as fraud
        if models.fraud_model.objects.filter(username=uname).exists():
            return redirect('fraud')

        user = authenticate(username=uname, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            context['warning'] = "Invalid login credentials. Please try again."

    return render(request, "login.html", context)


def register(request):
    """Handles user registration with validation."""
    values = {}

    if request.method == "POST":
        fname = request.POST.get('fname', '').strip()
        uname = request.POST.get('uname', '').strip().upper()
        email = request.POST.get('email', '').strip()
        pass1 = request.POST.get('password', '').strip()
        pass2 = request.POST.get('confirmpassword', '').strip()

        # Validation checks
        if User.objects.filter(username__iexact=uname).exists():
            values['exists'] = "Roll No already exists."
        elif not uname:
            values['exists'] = "Roll No is required."
        elif not fname:
            values['teamerr'] = "Team Name is required."
        elif not email:
            values['emailerr'] = "Email is required."
        elif not pass1:
            values['passerr'] = "Password is required."
        elif pass1 != pass2:
            values['passerr'] = "Passwords do not match."
        else:
            # Create new user
            user = User.objects.create_user(username=uname, password=pass1, first_name=fname, email=email)
            user.save()
            return redirect('login')  # Redirect to login page after successful registration

    return render(request, "register.html", values)


def user_logout(request):
    """Logs out the user and redirects to home."""
    logout(request)
    return redirect('home')


from .models import ExamControl

@login_required
def home(request):
    user = request.user

    # Check if the exam is started
    exam_control = ExamControl.objects.first()
    if not exam_control or not exam_control.exam_started:
        return render(request, 'exam_not_started.html')  # Render the new HTML page

    # Check if the user has already completed the exam
    if models.leaderboard.objects.filter(username=user.username).exists():
        return HttpResponse("Your exam is completed.")

    # Fetch and shuffle questions
    questions = list(models.question.objects.all())
    random.shuffle(questions)

    if request.method == 'POST':
        score = 0
        for i, question in enumerate(questions, start=1):
            selected_option = request.POST.get(f'question_{i}')
            correct_option = question.co

            if selected_option and selected_option == correct_option:
                score += 1

        models.leaderboard.objects.create(username=user.username, score=score)
        return HttpResponse("Your exam is completed.")

    return render(request, 'home.html', {'questions': questions})
from django.http import JsonResponse
import json

@login_required
def report_fraud(request):
    """API to flag users who switch tabs during the exam."""
    if request.method == "POST":
        uname = request.user.username
        
        # Flag user as fraud in the database
        if not models.fraud_model.objects.filter(username=uname).exists():
            models.fraud_model.objects.create(username=uname, fraud=True)
            logout(request)  # Force logout

        return JsonResponse({"status": "fraud_detected"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def leaderboard(request):
    """Displays the top 10 users on the leaderboard."""
    top_scores = models.leaderboard.objects.all().order_by('-score')[:10]
    return render(request, 'leaderboard.html', {'leaderboard_entries': top_scores})


def fraud(request):
    """Renders the fraud detection page and logs out the user."""
    uname = request.user.username

    if uname and not models.fraud_model.objects.filter(username=uname).exists():
        models.fraud_model.objects.create(username=uname, fraud=True)
        logout(request)  # Force logout

    return render(request, 'fraud.html')

