from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import random, time
from django.utils.timezone import now
from . import models
from .models import ExamControl, UserQuizProgress

def user_login(request):
    """Handles user authentication and prevents fraud users from logging in."""
    context = {}

    if request.method == "POST":
        uname = request.POST.get('uname', '').strip().upper()
        password = request.POST.get('password', '').strip()

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
            user = User.objects.create_user(username=uname, password=pass1, first_name=fname, email=email)
            user.save()
            return redirect('login')

    return render(request, "register.html", values)


def user_logout(request):
    """Logs out the user and redirects to home."""
    logout(request)
    return redirect('home')


@login_required
def home(request):
    user = request.user
    exam_control = ExamControl.objects.first()

    # Check if the exam has started
    if not exam_control or not exam_control.exam_started:
        return render(request, 'exam_not_started.html')

    # If user already has a leaderboard entry, redirect to exam_completed
    if models.leaderboard.objects.filter(username=user.username).exists():
        return redirect('examcompleted')

    # Fetch or create UserQuizProgress for this user
    quiz_progress, created = UserQuizProgress.objects.get_or_create(user=user)
    if created:
        # Set quiz duration to 15 minutes = 900 seconds
        quiz_progress.quiz_duration = 900  # 15 minutes
        quiz_progress.quiz_start_time = int(time.time())  # store the start as a UNIX timestamp
        quiz_progress.save()
    else:
        # If quiz_progress already exists but has no start time, set it now
        if quiz_progress.quiz_start_time is None:
            quiz_progress.quiz_start_time = int(time.time())
            quiz_progress.quiz_duration = 900  # 15 minutes
            quiz_progress.save()

    # Calculate elapsed and remaining time
    elapsed_time = int(time.time()) - quiz_progress.quiz_start_time
    remaining_time = max(quiz_progress.quiz_duration - elapsed_time, 0)

    # Auto-submit if time has run out
    if remaining_time <= 0:
        return redirect('examcompleted')

    # Shuffle questions if not already stored in session
    if 'shuffled_questions' not in request.session:
        questions = list(models.Question.objects.all())
        random.shuffle(questions)
        request.session['shuffled_questions'] = [q.id for q in questions]
    else:
        questions = list(models.Question.objects.filter(id__in=request.session['shuffled_questions']))

    # Handle POST submission
    if request.method == 'POST':
        # Calculate score
        score = sum(
            1 for question in questions
            if request.POST.get(f'question_{question.qno}') == question.co
        )
        # Update or create leaderboard entry
        models.leaderboard.objects.update_or_create(username=user.username, defaults={'score': score})
        return redirect('examcompleted')

    # Pass remaining_time to template for timer
    return render(request, 'home.html', {'questions': questions, 'remaining_time': remaining_time})


@login_required
def exam_completed(request):
    """Renders an animated exam completion page."""
    return render(request, 'examcompleted.html')


@login_required
def report_fraud(request):
    """API to flag users who switch tabs or resize window."""
    if request.method == "POST":
        uname = request.user.username
        if not models.fraud_model.objects.filter(username=uname).exists():
            models.fraud_model.objects.create(username=uname, fraud=True)
            logout(request)
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
        logout(request)
    return render(request, 'fraud.html')
