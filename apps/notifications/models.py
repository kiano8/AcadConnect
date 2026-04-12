from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('deadline', 'Deadline Alert'),
        ('grade', 'Grade Alert'),
        ('wellness', 'Wellness Reminder'),
        ('system', 'System'),
        ('goal', 'Goal Reminder'),
        ('habit', 'Habit Reminder'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='system')
    read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.message[:50]}"


class ReminderRule(models.Model):
    TRIGGER_CHOICES = [
        ('24h', '24 hours before'),
        ('48h', '48 hours before'),
        ('1week', '1 week before'),
        ('custom', 'Custom'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminder_rules')
    name = models.CharField(max_length=100)
    trigger_type = models.CharField(max_length=10, choices=TRIGGER_CHOICES, default='24h')
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"
