from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification, ReminderRule


@login_required
def notification_center(request):
    notifications = Notification.objects.filter(user=request.user)
    unread = notifications.filter(read=False)
    unread.update(read=True)  # Mark all as read on open
    reminder_rules = ReminderRule.objects.filter(user=request.user)
    return render(request, 'notifications/center.html', {
        'notifications': notifications[:50],
        'reminder_rules': reminder_rules,
    })


@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.read = True
    notif.save()
    return redirect('notifications:center')


@login_required
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if request.method == 'POST':
        notif.delete()
    return redirect('notifications:center')


@login_required
def unread_count_api(request):
    count = Notification.objects.filter(user=request.user, read=False).count()
    return JsonResponse({'count': count})


@login_required
def add_reminder_rule(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'My Reminder')
        trigger_type = request.POST.get('trigger_type', '24h')
        ReminderRule.objects.create(user=request.user, name=name, trigger_type=trigger_type)
        messages.success(request, "Reminder rule added!")
    return redirect('notifications:center')


@login_required
def delete_reminder_rule(request, pk):
    rule = get_object_or_404(ReminderRule, pk=pk, user=request.user)
    if request.method == 'POST':
        rule.delete()
        messages.success(request, "Reminder rule deleted.")
    return redirect('notifications:center')
