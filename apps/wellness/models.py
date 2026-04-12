from django.db import models
from django.conf import settings
from django.utils import timezone


class MotivationalQuote(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('study', 'Study'),
        ('stress', 'Stress Relief'),
        ('achievement', 'Achievement'),
        ('wellness', 'Wellness'),
    ]
    text = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='general')

    def __str__(self):
        return f'"{self.text[:50]}..." - {self.author}'


class WellnessReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('hydration', 'Hydration'),
        ('break', 'Break'),
        ('meditation', 'Meditation'),
        ('exercise', 'Exercise'),
        ('sleep', 'Sleep'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wellness_reminders')
    reminder_type = models.CharField(max_length=15, choices=REMINDER_TYPE_CHOICES)
    time = models.TimeField()
    active = models.BooleanField(default=True)
    message = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.get_reminder_type_display()} at {self.time}"


class StressLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stress_logs')
    stress_level = models.IntegerField(help_text="1-10 scale")
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - Stress {self.stress_level} on {self.date}"


class PersonalizedTip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tips')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    dismissed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
