from django import forms
from .models import Goal, Habit


class GoalForm(forms.ModelForm):
    target_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        required=False,
        help_text="Give your goal a target date to stay accountable (optional)."
    )

    class Meta:
        model = Goal
        fields = ['title', 'description', 'goal_type', 'target_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Read 2 books this month, Raise GPA to 3.5…',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Why is this goal important? What does success look like?',
            }),
            'goal_type': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'title': 'A clear, specific goal. Use action words — start with a verb.',
            'description': 'Optional. Describe your motivation or outline the steps.',
            'goal_type': 'Categorise your goal to group and filter it easily.',
        }


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'description', 'frequency', 'category', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Morning run, 30-min reading, No phone after 10 PM…',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describe when, how, or why you do this habit.',
            }),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control',
            }),
        }
        help_texts = {
            'name': 'Short, action-oriented habit name. Start small!',
            'description': 'Optional. Add context like time of day or cue.',
            'frequency': 'How often will you practice this habit?',
            'category': 'Group similar habits together for easy tracking.',
            'color': 'Colour used in your habit tracker.',
        }
