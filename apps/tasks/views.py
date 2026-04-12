from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Task, Subject
from .forms import TaskForm, SubjectForm
from apps.core.ai_engine import extract_tasks_from_text


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).select_related('subject')
    status_filter = request.GET.get('status', '')
    subject_filter = request.GET.get('subject', '')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if subject_filter:
        tasks = tasks.filter(subject__id=subject_filter)

    # Update overdue status on ALL pending tasks (independent of current filter)
    now = timezone.now()
    Task.objects.filter(user=request.user, deadline__lt=now, status='pending').update(status='overdue')

    subjects = Subject.objects.filter(user=request.user)
    context = {
        'tasks': tasks,
        'subjects': subjects,
        'status_filter': status_filter,
        'subject_filter': subject_filter,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f"Task '{task.title}' created successfully! ✅")
            return redirect('tasks:list')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated!")
            return redirect('tasks:list')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Edit', 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect('tasks:list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = 'completed'
    task.save()
    messages.success(request, f"'{task.title}' marked as complete! 🎉")
    return redirect('tasks:list')


@login_required
def task_api_countdown(request):
    """API endpoint: returns task countdown data as JSON."""
    tasks = Task.objects.filter(user=request.user).exclude(status='completed')
    data = [
        {
            'id': t.id,
            'title': t.title,
            'deadline': t.deadline.isoformat(),
            'color': t.color_label,
            'time_remaining': t.time_remaining_display,
        }
        for t in tasks
    ]
    return JsonResponse({'tasks': data})


@login_required
def subject_list(request):
    subjects = Subject.objects.filter(user=request.user)
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.user = request.user
            subject.save()
            messages.success(request, f"Subject '{subject.name}' added!")
            return redirect('tasks:subjects')
    else:
        form = SubjectForm()
    return render(request, 'tasks/subjects.html', {'subjects': subjects, 'form': form})


@login_required
def extract_tasks_view(request):
    """NLP task extraction from pasted syllabus text."""
    extracted = []
    if request.method == 'POST':
        text = request.POST.get('syllabus_text', '')
        extracted = extract_tasks_from_text(text)
    return render(request, 'tasks/extract_tasks.html', {'extracted': extracted})
