from django.db import models
from django.conf import settings
from django.utils import timezone


class Goal(models.Model):
    GOAL_TYPE_CHOICES = [
        ('short', 'Short-term'),
        ('long', 'Long-term'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=10, choices=GOAL_TYPE_CHOICES, default='short')
    target_date = models.DateField(null=True, blank=True)
    progress = models.IntegerField(default=0, help_text="0-100 percent")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def days_remaining(self):
        if self.target_date:
            delta = self.target_date - timezone.now().date()
            return delta.days
        return None


class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    CATEGORY_CHOICES = [
        ('study', 'Study'),
        ('health', 'Health'),
        ('wellness', 'Wellness'),
        ('social', 'Social'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='other')
    color = models.CharField(max_length=7, default='#2A9D8F')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def current_streak(self):
        from datetime import date, timedelta
        logs = self.logs.filter(completed=True).order_by('-date')
        if not logs.exists():
            return 0
        streak = 0
        check_date = date.today()
        for log in logs:
            if log.date == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        return streak

    @property
    def completed_today(self):
        return self.logs.filter(date=timezone.now().date(), completed=True).exists()


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['habit', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.name} - {self.date}"
