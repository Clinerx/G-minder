from django.urls import path
from . import views

urlpatterns = [
    path('', views.landingPage, name='landing'),
    path('landingPage', views.landingPage, name='homeBase'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('progressPage/', views.progressPage, name='progressPage'),

    # Task Section
    path('todo_list/', views.todo_list, name='todo_list'),
    path('task/<int:task_id>/', views.add_or_update_task, name='add_or_update_task'),  # Add this line for the update task view
    path('add_task/', views.add_or_update_task, name='add_or_update_task'),  # This is for adding new task
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('complete_task/<int:task_id>/', views.complete_task, name='complete_task'),
    
    # Other routes
    path('chat_with_gemini/', views.chat_with_gemini, name='chat_with_gemini'),
    path('mental/', views.mental_checkin, name='mental-checkin'),
    path('mental/', views.mental_checkin, name='mental'),


]
