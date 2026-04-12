from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Event, ClassSchedule
from .forms import EventForm, ClassScheduleForm
from apps.core.ai_engine import detect_free_slots, suggest_activities


@login_required
def calendar_view(request):
    class_schedules = ClassSchedule.objects.filter(user=request.user)
    return render(request, 'schedule/calendar.html', {'class_schedules': class_schedules})


@login_required
def events_api(request):
    """Return events as JSON for FullCalendar."""
    events = Event.objects.filter(user=request.user)
    data = []
    for e in events:
        data.append({
            'id': e.id,
            'title': e.title,
            'start': e.start_datetime.isoformat(),
            'end': e.end_datetime.isoformat(),
            'color': e.color,
            'allDay': e.all_day,
            'extendedProps': {'type': e.event_type, 'description': e.description},
        })
    # Add class schedules as recurring events
    from datetime import datetime, timedelta
    today = timezone.now().date()
    for cls in ClassSchedule.objects.filter(user=request.user):
        # Find next 30 days of this class
        for i in range(30):
            d = today + timedelta(days=i)
            if d.weekday() == cls.day_of_week:
                start = timezone.make_aware(datetime.combine(d, cls.start_time))
                end = timezone.make_aware(datetime.combine(d, cls.end_time))
                data.append({
                    'title': f"[Class] {cls.course_name}",
                    'start': start.isoformat(),
                    'end': end.isoformat(),
                    'color': cls.color,
                    'editable': False,
                })
    return JsonResponse(data, safe=False)


@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, f"Event '{event.title}' added! 📅")
            return redirect('schedule:calendar')
    else:
        form = EventForm()
    return render(request, 'schedule/event_form.html', {'form': form, 'action': 'Add'})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated!")
            return redirect('schedule:calendar')
    else:
        form = EventForm(instance=event)
    return render(request, 'schedule/event_form.html', {'form': form, 'action': 'Edit', 'event': event})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted.")
        return redirect('schedule:calendar')
    return render(request, 'schedule/event_confirm_delete.html', {'event': event})


@login_required
def class_schedule_view(request):
    schedules = ClassSchedule.objects.filter(user=request.user).order_by('day_of_week', 'start_time')
    if request.method == 'POST':
        form = ClassScheduleForm(request.POST)
        if form.is_valid():
            cls = form.save(commit=False)
            cls.user = request.user
            cls.save()
            messages.success(request, f"Class '{cls.course_name}' added to your schedule!")
            return redirect('schedule:classes')
    else:
        form = ClassScheduleForm()
    return render(request, 'schedule/classes.html', {'schedules': schedules, 'form': form})


@login_required
def free_time_view(request):
    today = timezone.now().date()
    free_slots = detect_free_slots(request.user, today)
    suggestions = suggest_activities(free_slots, request.user)
    return render(request, 'schedule/free_time.html', {
        'free_slots': free_slots,
        'suggestions': suggestions,
        'today': today,
    })
