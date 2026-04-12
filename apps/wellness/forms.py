from django import forms
from .models import StressLog, WellnessReminder


class StressLogForm(forms.ModelForm):
    class Meta:
        model = StressLog
        fields = ['stress_level', 'note']
        widgets = {
            'stress_level': forms.NumberInput(attrs={
                'min': 1,
                'max': 10,
                'type': 'range',
                'class': 'form-control',
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': "What's contributing to your stress today? Vent a little…",
            }),
        }
        help_texts = {
            'stress_level': 'Slide to rate: 1 = calm & relaxed, 10 = completely overwhelmed.',
            'note': 'Optional. Writing it out can help you process it.',
        }


class WellnessReminderForm(forms.ModelForm):
    class Meta:
        model = WellnessReminder
        fields = ['reminder_type', 'time', 'message']
        widgets = {
            'reminder_type': forms.Select(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'message': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Drink a full glass of water! Take a deep breath.',
            }),
        }
        help_texts = {
            'reminder_type': 'What kind of wellness check-in is this?',
            'time': 'At what time should this reminder trigger?',
            'message': 'A short, encouraging note to yourself (optional).',
        }
