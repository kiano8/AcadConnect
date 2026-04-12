from django.db import models
from django.conf import settings


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('class', 'Class'),
        ('assignment', 'Assignment'),
        ('personal', 'Personal'),
        ('extracurricular', 'Extracurricular'),
        ('study', 'Study Session'),
        ('exam', 'Exam'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES, default='personal')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#4A90D9')
    all_day = models.BooleanField(default=False)
    recurrence = models.CharField(max_length=20, blank=True, choices=[
        ('', 'None'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')
    ])

    def __str__(self):
        return f"{self.title} ({self.start_datetime.date()})"

    @property
    def duration_hours(self):
        delta = self.end_datetime - self.start_datetime
        return delta.total_seconds() / 3600


class ClassSchedule(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_schedules')
    course_name = models.CharField(max_length=100)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    professor = models.CharField(max_length=100, blank=True)
    semester = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=7, default='#0D3B66')

    def __str__(self):
        return f"{self.course_name} - {self.get_day_of_week_display()}"
