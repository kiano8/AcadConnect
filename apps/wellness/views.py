from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import random
from .models import MotivationalQuote, WellnessReminder, StressLog, PersonalizedTip
from .forms import StressLogForm, WellnessReminderForm
from apps.core.ai_engine import get_personalized_tip


@login_required
def wellness_hub(request):
    user = request.user
    today = timezone.now().date()

    # Get or create today's stress log
    stress_log, _ = StressLog.objects.get_or_create(
        user=user, date=today, defaults={'stress_level': 5}
    )

    # Get motivational quote based on stress
    if user.stress_level >= 7:
        quotes = MotivationalQuote.objects.filter(category='stress')
    else:
        quotes = MotivationalQuote.objects.all()
    quote = random.choice(list(quotes)) if quotes.exists() else None

    # Personalized tip
    tip = get_personalized_tip(user)

    # Wellness reminders
    reminders = WellnessReminder.objects.filter(user=user, active=True)

    # Stress history for chart
    stress_history = StressLog.objects.filter(user=user).order_by('-date')[:14]

    stress_form = StressLogForm(instance=stress_log)
    reminder_form = WellnessReminderForm()

    return render(request, 'wellness/wellness_hub.html', {
        'quote': quote,
        'tip': tip,
        'reminders': reminders,
        'stress_log': stress_log,
        'stress_form': stress_form,
        'reminder_form': reminder_form,
        'stress_history': list(reversed(list(stress_history))),
    })


@login_required
def log_stress(request):
    if request.method == 'POST':
        today = timezone.now().date()
        stress_log, _ = StressLog.objects.get_or_create(user=request.user, date=today)
        form = StressLogForm(request.POST, instance=stress_log)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.date = today
            log.save()
            # Update user's stress level
            request.user.stress_level = log.stress_level
            request.user.save()
            messages.success(request, "Stress level logged. Take care of yourself! 💙")
    return redirect('wellness:hub')


@login_required
def add_reminder(request):
    if request.method == 'POST':
        form = WellnessReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            messages.success(request, "Wellness reminder set!")
    return redirect('wellness:hub')


@login_required
def toggle_reminder(request, pk):
    reminder = get_object_or_404(WellnessReminder, pk=pk, user=request.user)
    reminder.active = not reminder.active
    reminder.save()
    return redirect('wellness:hub')
