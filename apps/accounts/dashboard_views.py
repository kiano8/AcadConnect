from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.tasks.models import Task
from apps.grades.models import Course
from apps.habits.models import Habit
from apps.notifications.models import Notification
from apps.wellness.models import MotivationalQuote, StressLog
from apps.core.ai_engine import prioritize_tasks, predict_gpa, detect_free_slots, suggest_activities, get_personalized_tip
import random


@login_required
def home(request):
    user = request.user
    now = timezone.now()

    # Tasks summary
    pending_tasks = Task.objects.filter(user=user).exclude(status='completed').order_by('deadline')[:5]
    overdue_count = Task.objects.filter(user=user, deadline__lt=now).exclude(status='completed').count()
    due_today = Task.objects.filter(
        user=user,
        deadline__date=now.date()
    ).exclude(status='completed').count()

    # Grades
    courses = Course.objects.filter(user=user)
    current_gpa = predict_gpa(user)

    # Habits
    habits = Habit.objects.filter(user=user, active=True)
    habits_completed_today = sum(1 for h in habits if h.completed_today)

    # Notifications
    unread_notifications = Notification.objects.filter(user=user, read=False).count()
    recent_notifications = Notification.objects.filter(user=user)[:5]

    # Motivational quote
    quote = None
    stress_level = user.stress_level
    if stress_level >= 7:
        quotes = MotivationalQuote.objects.filter(category='stress')
    else:
        quotes = MotivationalQuote.objects.all()
    if quotes.exists():
        quote = random.choice(list(quotes))

    # Personalized tip
    tip = get_personalized_tip(user)

    # Free time slots for today
    free_slots = detect_free_slots(user, now.date())
    suggestions = suggest_activities(free_slots, user)[:2]

    # Smart task priority
    smart_tasks = prioritize_tasks(user)[:5]

    context = {
        'pending_tasks': pending_tasks,
        'overdue_count': overdue_count,
        'due_today': due_today,
        'courses': courses,
        'current_gpa': current_gpa,
        'habits': habits,
        'habits_completed_today': habits_completed_today,
        'total_habits': habits.count(),
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
        'quote': quote,
        'tip': tip,
        'free_slots': free_slots[:3],
        'suggestions': suggestions,
        'smart_tasks': smart_tasks,
        'now': now,
    }
    return render(request, 'dashboard/home.html', context)
