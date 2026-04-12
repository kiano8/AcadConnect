from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Goal, Habit, HabitLog
from .forms import GoalForm, HabitForm


@login_required
def goals_view(request):
    goals = Goal.objects.filter(user=request.user).order_by('status', 'target_date')
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, f"Goal '{goal.title}' set! 🎯")
            return redirect('habits:goals')
    else:
        form = GoalForm()
    return render(request, 'habits/goals.html', {'goals': goals, 'form': form})


@login_required
def goal_update_progress(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        progress = int(request.POST.get('progress', goal.progress))
        goal.progress = min(100, max(0, progress))
        if goal.progress == 100:
            goal.status = 'completed'
        goal.save()
        messages.success(request, f"Progress updated to {goal.progress}%!")
    return redirect('habits:goals')


@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Goal deleted.")
    return redirect('habits:goals')


@login_required
def habits_view(request):
    habits = Habit.objects.filter(user=request.user, active=True)
    today = timezone.now().date()

    # Pre-check today's logs
    habit_status = {}
    for habit in habits:
        log, _ = HabitLog.objects.get_or_create(habit=habit, date=today)
        habit_status[habit.id] = log.completed

    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, f"Habit '{habit.name}' added! 🌱")
            return redirect('habits:habits')
    else:
        form = HabitForm()

    return render(request, 'habits/habits.html', {
        'habits': habits,
        'habit_status': habit_status,
        'today': today,
        'form': form,
    })


@login_required
def habit_check(request, pk):
    if request.method != 'POST':
        return redirect('habits:habits')
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = timezone.now().date()
    log, created = HabitLog.objects.get_or_create(habit=habit, date=today)
    log.completed = not log.completed
    log.save()
    status = "completed" if log.completed else "unchecked"
    messages.success(request, f"'{habit.name}' marked as {status}! 🔥" if log.completed else f"'{habit.name}' unchecked.")
    return redirect('habits:habits')


@login_required
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, "Habit removed.")
    return redirect('habits:habits')
