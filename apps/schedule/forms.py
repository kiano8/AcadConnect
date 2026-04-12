from django import forms
from .models import Event, ClassSchedule


class EventForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        help_text="When does this event start?"
    )
    end_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        help_text="When does this event end? Must be after the start time."
    )

    class Meta:
        model = Event
        fields = ['title', 'event_type', 'start_datetime', 'end_datetime', 'description', 'color', 'all_day']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Midterm Exam, Study Group, Team Meeting…',
                'autofocus': True,
            }),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any details, location, meeting link, or notes…',
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control',
            }),
            'all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'title': 'A short, clear title for this event.',
            'event_type': 'Categorise the event to keep your calendar organised.',
            'description': 'Optional. Add location, notes, or a meeting link.',
            'color': 'Choose a colour for this event on the calendar.',
            'all_day': 'Check this if the event spans the whole day (no specific time).',
        }


class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['course_name', 'day_of_week', 'start_time', 'end_time', 'room', 'professor', 'semester', 'color']
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Introduction to Psychology, Calculus 2…',
            }),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'room': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Room 204, Science Building B',
            }),
            'professor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Dr. Santos, Prof. Reyes',
            }),
            'semester': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 1st Semester 2025–2026',
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control',
            }),
        }
        help_texts = {
            'course_name': 'Full name of the course or subject.',
            'day_of_week': 'Which day of the week does this class meet?',
            'start_time': 'What time does the class begin?',
            'end_time': 'What time does the class end?',
            'room': 'Room number or building location (optional).',
            'professor': "Your professor's or instructor's name (optional).",
            'semester': 'Academic term this class belongs to (optional).',
            'color': 'Colour shown for this class on your calendar.',
        }
