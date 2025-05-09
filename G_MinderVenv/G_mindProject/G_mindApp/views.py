from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Task
from django.utils.timezone import now
from django.contrib.auth import logout
from django.shortcuts import redirect

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Task
from .forms import TaskForm, UpdateTaskForm, MentalHealthEntryForm
from django.core.paginator import Paginator
from .forms import CustomUserRegistrationForm, LoginForm
from .models import Task
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import random

logger = logging.getLogger(__name__)
@csrf_exempt
def chat_with_gemini(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get('message')

        # Send the user message to Gemini (you must replace with actual Gemini API endpoint)
        api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyD4omIHssBE-iKB3NUCPzuvQTUA4xzBoOA"
        payload = {
            "contents": [{
                "parts": [{
                    "text": user_message
                }]
            }]
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, headers=headers, json=payload)
        result = response.json()

        # Extract the AI's reply
        try:
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            ai_response = "Sorry, something went wrong."

        return JsonResponse({"reply": ai_response})


# ^ Templates Pages ===========================>


def landingPage(request):
    return render(request, 'user_authentication_folder/landingPage.html')

# View to update failed tasks automatically
def update_failed_tasks():
    tasks = Task.objects.filter(completed=False, due_date__lte=timezone.now())
    for task in tasks:
        task.status = Task.Status.FAILED
        task.save()

@login_required
def todo_list(request):
    update_failed_tasks()

    user = request.user
    tasks = Task.objects.filter(user=user)
    form = TaskForm()

    completed_tasks = tasks.filter(status=Task.Status.COMPLETED)
    ongoing_tasks = tasks.filter(status=Task.Status.IN_PROGRESS)
    failed_tasks = tasks.filter(status=Task.Status.FAILED)

    total_tasks = tasks.count()
    completed_tasks_count = completed_tasks.count()
    progress = round((completed_tasks_count / total_tasks * 100)) if total_tasks > 0 else 0

    today = timezone.now()

    # Pagination for completed tasks
    paginator = Paginator(completed_tasks, 3)  # Show 5 completed tasks per page
    page_number = request.GET.get('page')
    completed_tasks_page = paginator.get_page(page_number)

    # Daily progress
    daily_tasks = tasks.filter(created_at__date=today.date())
    daily_completed_tasks = daily_tasks.filter(status=Task.Status.COMPLETED).count()
    daily_progress = round((daily_completed_tasks / 10) * 100) if daily_tasks.exists() else 0
    daily_remaining = max(10 - daily_completed_tasks, 0)

    # Weekly progress
    start_of_week = today - timedelta(days=today.weekday())
    week_tasks = tasks.filter(created_at__gte=start_of_week)
    week_completed_tasks = week_tasks.filter(status=Task.Status.COMPLETED).count()
    week_progress = round((week_completed_tasks / 20) * 100) if week_tasks.exists() else 0
    week_remaining = max(20 - week_completed_tasks, 0)

    # Monthly progress
    start_of_month = today.replace(day=1)
    month_tasks = tasks.filter(created_at__gte=start_of_month)
    month_completed_tasks = month_tasks.filter(status=Task.Status.COMPLETED).count()
    month_progress = round((month_completed_tasks / 50) * 100) if month_tasks.exists() else 0
    month_remaining = max(50 - month_completed_tasks, 0)

    # Add forms to ongoing tasks for editing
    for task in ongoing_tasks:
        task.get_form = TaskForm(instance=task)

    context = {
        'form': form,
        'tasks': tasks,
        'completed_tasks': completed_tasks_page,  # use paginated version here
        'ongoing_tasks': ongoing_tasks,
        'failed_tasks': failed_tasks,
        'progress': progress,
        'daily_progress': daily_progress,
        'daily_remaining': daily_remaining,
        'week_progress': week_progress,
        'week_remaining': week_remaining,
        'month_progress': month_progress,
        'month_remaining': month_remaining,
        'daily_limit': 10,
        'weekly_limit': 20,
        'monthly_limit': 50,
    }

    return render(request, 'user_authentication_folder/progress.html', context)


def logout_view(request):
    logout(request)
    return redirect('landing')  # Redirect to the landing page after logging out

@login_required
def progressPage(request):
    form = TaskForm()
    tasks = Task.objects.filter(user=request.user)
    now = timezone.now()

    # Update task statuses
    for task in tasks:
        if task.completed:
            task.status = Task.Status.COMPLETED
        elif task.due_date and task.due_date <= now:
            task.status = Task.Status.FAILED
        else:
            task.status = Task.Status.IN_PROGRESS
        task.save()

    # Re-fetch updated tasks
    tasks = Task.objects.filter(user=request.user)
    completed_tasks = tasks.filter(status=Task.Status.COMPLETED)
    ongoing_tasks = tasks.filter(status=Task.Status.IN_PROGRESS)
    failed_tasks = tasks.filter(status=Task.Status.FAILED)

    total_tasks = tasks.count()
    completed_count = completed_tasks.count()
    progress = round((completed_count / total_tasks * 100)) if total_tasks > 0 else 0

    today = now.date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Daily Progress
    daily_tasks = tasks.filter(created_at__date=today)
    daily_completed = daily_tasks.filter(completed=True).count()
    daily_progress = round((daily_completed / 10) * 100) if daily_tasks.exists() else 0
    daily_remaining = max(10 - daily_completed, 0)

    # Weekly Progress
    weekly_tasks = tasks.filter(created_at__date__gte=start_of_week)
    weekly_completed = weekly_tasks.filter(completed=True).count()
    week_progress = round((weekly_completed / 20) * 100) if weekly_tasks.exists() else 0
    week_remaining = max(20 - weekly_completed, 0)

    # Monthly Progress
    monthly_tasks = tasks.filter(created_at__date__gte=start_of_month)
    monthly_completed = monthly_tasks.filter(completed=True).count()
    month_progress = round((monthly_completed / 50) * 100) if monthly_tasks.exists() else 0
    month_remaining = max(50 - monthly_completed, 0)

    context = {
        'form': form,
        'completed_tasks': completed_tasks,
        'ongoing_tasks': ongoing_tasks,
        'failed_tasks': failed_tasks,
        'progress': progress,
        'daily_progress': daily_progress,
        'daily_remaining': daily_remaining,
        'week_progress': week_progress,
        'week_remaining': week_remaining,
        'month_progress': month_progress,
        'month_remaining': month_remaining,
    }

    return render(request, 'user_authentication_folder/progress.html', context)


# View to add or update a task
@login_required
def add_or_update_task(request, task_id=None):
    if task_id:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        form = TaskForm(request.POST or None, instance=task)
    else:
        form = TaskForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)  

        if not task_id:
            task.user = request.user  # Only assign user if creating a new task

        # Assign status based on due_date and completion
        now = timezone.now()
        if task.completed:
            task.status = Task.Status.COMPLETED
        elif task.due_date and task.due_date <= now:
            task.status = Task.Status.FAILED
        else:
            task.status = Task.Status.IN_PROGRESS  # Default to IN_PROGRESS for valid future tasks

        task.save()

        # After saving, redirect to the todo list page with updated tasks
        return redirect('todo_list')  # Replace with your actual redirect path

    # Pass ongoing tasks into context for rendering
    ongoing_tasks = Task.objects.filter(user=request.user, status=Task.Status.IN_PROGRESS)  # Filter tasks by the logged-in user
    return render(request, 'user_authentication_folder/progress.html', {
        'form': form,
        'task_id': task_id,
        'ongoing_tasks': ongoing_tasks,  # Include ongoing tasks here
    })


# View to mark task as completed
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.status = Task.Status.COMPLETED
    task.completed = True
    task.save()
    return redirect('todo_list')

# View to delete a task
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('todo_list')
# ^ ================================>

# ^ Authentication Section ======================>

@login_required
def user_dashboard(request):
    today = timezone.now().date()
    now = timezone.now()

    tasks = Task.objects.filter(user=request.user)
    today_tasks = tasks.filter(created_at__date=today)
    today_completed = today_tasks.filter(completed=True).count()

    # General task list for display
    display_tasks = tasks.order_by('-created_at')[:5]  # Latest 3 tasks

    # Weekly Progress
    start_of_week = today - timedelta(days=today.weekday())
    week_tasks = tasks.filter(created_at__date__gte=start_of_week)
    week_completed = week_tasks.filter(completed=True).count()

    # ✨ Daily Focus Suggestions
    focus_suggestions = [
        "Complete 2 major tasks without distractions",
        "Take 5-minute breaks every hour",
        "Avoid multitasking, focus on one thing at a time",
        "Stay hydrated and take a walk after lunch",
        "Finish one long-pending task today",
        "Practice deep breathing for 2 minutes before working",
        "Review your progress and reward yourself",
        "Disconnect from your phone while working",
        "Organize your workspace for clarity",
        "Write down 3 things you're grateful for"
    ]
    index = today.day % len(focus_suggestions)
    daily_focus = focus_suggestions[index]

    context = {
        'user_name': request.user.username,
        'tasks': display_tasks,
        'today_completed': today_completed,
        'week_completed': week_completed,
        'weekly_limit': 20,
        'daily_focus': daily_focus,  # 👈 Add this to the context
    }

    return render(request, 'user_authentication_folder/user_dashboard.html', context)

def register_user(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('/')  # Redirect to homepage or dashboard
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'user_authentication_folder/landingPage.html', {'form': form})  # Assuming you're using modals on index.html

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # this could be email or username
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('user_dashboard')  # or your actual dashboard URL name
        else:
            messages.error(request, "Invalid email/username or password.")
            return render(request, 'user_authentication_folder/landingPage.html')  # re-render the home with the modal open

    return redirect('user_dashboard')

# ^ ======================================================>>
def get_daily_focus():
    suggestions = [
        "Complete 2 major tasks without distractions",
        "Take 5-minute breaks every hour",
        "Avoid multitasking, focus on one thing at a time",
        "Stay hydrated and take a walk after lunch",
        "Finish one long-pending task today",
        "Practice deep breathing for 2 minutes before working",
        "Review your progress and reward yourself",
        "Disconnect from your phone while working",
        "Organize your workspace for clarity",
        "Write down 3 things you're grateful for"
    ]

    # Select one based on the day (e.g., rotating daily)
    index = datetime.now().day % len(suggestions)
    return suggestions[index]


@login_required
def mental_checkin(request):
    if request.method == 'POST':
        form = MentalHealthEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('mental-checkin')# or wherever you want to redirect after saving
    else:
        form = MentalHealthEntryForm()
    
    return render(request, 'user_authentication_folder/mental.html', {'form': form})
