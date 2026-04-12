from django import forms
from .models import Task, Subject


class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        help_text="Set a deadline so the AI can calculate urgency and remind you in time."
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'subject', 'deadline', 'priority', 'difficulty', 'status', 'file_attachment', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Write Chapter 3 essay, Finish lab report…',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What does this task involve? Any specific requirements or steps?',
            }),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'file_attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any syllabus notes, references, or reminders for this task?',
            }),
        }
        help_texts = {
            'title': 'Keep it short and action-oriented — you should know exactly what to do at a glance.',
            'description': 'Optional but helpful. List steps or clarify the scope.',
            'subject': 'Link this task to a subject to keep things organised.',
            'priority': '1 = Low, 5 = Critical. Used by the AI prioritiser.',
            'difficulty': '1 = Very easy, 5 = Very hard. Helps estimate effort.',
            'status': 'Update this as you make progress on the task.',
            'file_attachment': 'Attach a PDF, image, or document for reference.',
            'notes': 'Extracted syllabus notes, rubric details, or extra reminders.',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['subject'].queryset = Subject.objects.filter(user=user)
        self.fields['subject'].required = False
        self.fields['subject'].empty_label = '— No subject —'


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Mathematics, Biology, English Lit',
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control',
            }),
        }
        help_texts = {
            'name': 'A short, recognisable name for the subject.',
            'color': 'Pick a colour to identify tasks and schedule entries for this subject.',
        }
