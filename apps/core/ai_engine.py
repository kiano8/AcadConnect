"""
Core AI Engine for AcadConnect
Handles: task prioritization, GPA prediction, free slot detection, activity suggestions, NLP task extraction
"""
from datetime import datetime, timedelta, time
from django.utils import timezone
import re


def prioritize_tasks(user):
    """Return tasks sorted by a composite smart priority score."""
    from apps.tasks.models import Task
    tasks = Task.objects.filter(user=user).exclude(status='completed')
    return sorted(tasks, key=lambda t: t.smart_priority_score, reverse=True)


def predict_gpa(user):
    """
    Predict GPA trend using linear regression on grade snapshots.
    Returns predicted GPA as float, or current GPA if insufficient data.
    """
    from apps.grades.models import Course
    courses = Course.objects.filter(user=user)
    if not courses:
        return None

    total_points = 0
    total_credits = 0
    for course in courses:
        gp = course.grade_points
        if gp is not None:
            total_points += gp * course.credit_hours
            total_credits += course.credit_hours

    if total_credits == 0:
        return None

    current_gpa = total_points / total_credits

    # Try linear regression on snapshots if scikit-learn available
    try:
        import numpy as np
        from sklearn.linear_model import LinearRegression
        from apps.grades.models import GradeSnapshot

        all_snapshots = GradeSnapshot.objects.filter(course__user=user).order_by('timestamp')
        if all_snapshots.count() >= 3:
            base_time = all_snapshots.first().timestamp
            X = np.array([(s.timestamp - base_time).total_seconds() / 86400 for s in all_snapshots]).reshape(-1, 1)
            y = np.array([s.computed_grade for s in all_snapshots])
            model = LinearRegression().fit(X, y)
            future_days = 30
            predicted_grade = model.predict([[X[-1][0] + future_days]])[0]
            # Convert percentage grade to GPA roughly
            predicted_gpa = max(0.0, min(4.0, (predicted_grade / 100) * 4.0))
            return round(predicted_gpa, 2)
    except Exception:
        pass

    return round(current_gpa, 2)


def detect_free_slots(user, target_date=None):
    """
    Scan user's schedule for a given date and return free time windows >= 30 min.
    Returns list of (start_time, end_time) tuples.
    """
    from apps.schedule.models import Event, ClassSchedule

    if target_date is None:
        target_date = timezone.now().date()

    day_start = timezone.make_aware(datetime.combine(target_date, time(8, 0)))
    day_end = timezone.make_aware(datetime.combine(target_date, time(22, 0)))

    # Collect all occupied windows
    occupied = []

    # From events
    events = Event.objects.filter(
        user=user,
        start_datetime__date=target_date
    )
    for event in events:
        occupied.append((event.start_datetime, event.end_datetime))

    # From class schedules (recurring)
    day_number = target_date.weekday()
    classes = ClassSchedule.objects.filter(user=user, day_of_week=day_number)
    for cls in classes:
        start = timezone.make_aware(datetime.combine(target_date, cls.start_time))
        end = timezone.make_aware(datetime.combine(target_date, cls.end_time))
        occupied.append((start, end))

    # Sort and merge overlapping windows
    occupied.sort(key=lambda x: x[0])
    merged = []
    for window in occupied:
        if merged and window[0] <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], window[1]))
        else:
            merged.append(list(window))

    # Find free slots
    free_slots = []
    current = day_start
    for occ_start, occ_end in merged:
        if current < occ_start:
            duration = (occ_start - current).total_seconds() / 60
            if duration >= 30:
                free_slots.append({
                    'start': current,
                    'end': occ_start,
                    'duration_minutes': int(duration),
                })
        current = max(current, occ_end)

    if current < day_end:
        duration = (day_end - current).total_seconds() / 60
        if duration >= 30:
            free_slots.append({
                'start': current,
                'end': day_end,
                'duration_minutes': int(duration),
            })

    return free_slots


def suggest_activities(free_slots, user):
    """
    Suggest productive or relaxing activities based on slot duration and user stress level.
    """
    stress = getattr(user, 'stress_level', 5)
    suggestions = []

    study_activities = [
        "Review lecture notes for an upcoming exam",
        "Work on a pending assignment",
        "Read ahead for tomorrow's class",
        "Practice problems from your textbook",
        "Watch a tutorial on a tough topic",
    ]
    relax_activities = [
        "Take a walk and get some fresh air",
        "Listen to calming music or a podcast",
        "Do a 10-minute meditation session",
        "Stretch and do light exercises",
        "Journal your thoughts or doodle freely",
        "Enjoy a hobby you love",
    ]

    for slot in free_slots:
        duration = slot['duration_minutes']
        if stress >= 7:
            # High stress: suggest relaxation
            import random
            activity = random.choice(relax_activities)
            suggestion_type = 'relax'
        elif duration < 45:
            import random
            activity = random.choice(relax_activities)
            suggestion_type = 'relax'
        else:
            import random
            activity = random.choice(study_activities) if stress < 6 else random.choice(relax_activities)
            suggestion_type = 'study' if stress < 6 else 'relax'

        suggestions.append({
            'slot': slot,
            'activity': activity,
            'type': suggestion_type,
        })

    return suggestions


def extract_tasks_from_text(text):
    """
    Basic NLP-based task extraction from syllabus or pasted text.
    Returns list of dicts with 'title' and 'deadline_hint'.
    """
    extracted = []

    # Pattern: find lines with keywords like "due", "submit", "deadline", "assignment"
    task_patterns = [
        r'(?i)(assignment|homework|project|quiz|exam|lab|report|essay|presentation)[^\n]*',
        r'(?i)(?:due|submit|deadline)[^\n]*',
    ]

    date_patterns = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b',
        r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\.?\s+\d{1,2}\b',
    ]

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for pattern in task_patterns:
            match = re.search(pattern, line)
            if match:
                title = line[:100].strip()
                deadline_hint = None
                for dp in date_patterns:
                    dm = re.search(dp, line, re.IGNORECASE)
                    if dm:
                        deadline_hint = dm.group(0)
                        break
                extracted.append({
                    'title': title,
                    'deadline_hint': deadline_hint,
                })
                break

    return extracted[:20]  # Limit to 20 tasks


def get_personalized_tip(user):
    """Generate a personalized motivational tip based on user's current state."""
    from apps.tasks.models import Task
    from django.utils import timezone

    stress = getattr(user, 'stress_level', 5)
    now = timezone.now()

    overdue_count = Task.objects.filter(user=user, deadline__lt=now).exclude(status='completed').count()
    upcoming_count = Task.objects.filter(
        user=user,
        deadline__gte=now,
        deadline__lte=now + timedelta(days=2)
    ).exclude(status='completed').count()

    if overdue_count > 0:
        return f"You have {overdue_count} overdue task(s). Start with the smallest one — momentum is everything! 💪"
    elif upcoming_count >= 3 and stress >= 7:
        return "Heavy week ahead! Break big tasks into small chunks, and remember: one step at a time. You've got this! 🌟"
    elif upcoming_count > 0:
        return f"You have {upcoming_count} task(s) due soon. Block out focus time and tackle them early! ⏰"
    elif stress >= 8:
        return "High stress detected. Take a 10-minute break, breathe deeply, and come back refreshed. Your wellbeing matters! 🧘"
    else:
        return "You're on track! Keep building good habits and celebrate small wins along the way. 🎉"
