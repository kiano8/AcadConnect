from django.db import models
from django.conf import settings
from django.utils import timezone


class Subject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#4A90D9')

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [(i, str(i)) for i in range(1, 6)]
    DIFFICULTY_CHOICES = [(i, str(i)) for i in range(1, 6)]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_attachment = models.FileField(upload_to='task_files/', blank=True, null=True)
    notes = models.TextField(blank=True, help_text="Extracted syllabus notes or additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', '-priority']

    def __str__(self):
        return self.title

    @property
    def urgency_score(self):
        """Compute urgency: higher = more urgent. Based on time remaining."""
        now = timezone.now()
        delta = self.deadline - now
        hours_left = delta.total_seconds() / 3600
        if hours_left <= 0:
            return 10
        elif hours_left <= 24:
            return 9
        elif hours_left <= 48:
            return 7
        elif hours_left <= 72:
            return 5
        elif hours_left <= 168:
            return 3
        return 1

    @property
    def smart_priority_score(self):
        """Combined score: urgency + priority + difficulty."""
        return self.urgency_score + self.priority + self.difficulty

    @property
    def is_overdue(self):
        return timezone.now() > self.deadline and self.status != 'completed'

    @property
    def color_label(self):
        if self.is_overdue:
            return '#E07A5F'
        score = self.urgency_score
        if score >= 9:
            return '#E07A5F'  # coral red
        elif score >= 7:
            return '#F4A261'  # orange
        elif score >= 5:
            return '#E9C46A'  # yellow
        elif score >= 3:
            return '#2A9D8F'  # teal
        return '#52B788'      # green

    @property
    def time_remaining_display(self):
        now = timezone.now()
        delta = self.deadline - now
        if delta.total_seconds() <= 0:
            return "Overdue"
        days = delta.days
        hours = delta.seconds // 3600
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {(delta.seconds % 3600) // 60}m"
        return f"{(delta.seconds % 3600) // 60}m"
