from django import forms
from django.contrib.auth import get_user_model
from .models import Group, GroupTask

User = get_user_model()


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Biology Study Group, Thesis Team…',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': "What is this group working on? What's the shared goal?",
            }),
        }
        help_texts = {
            'name': 'A clear name your group members will recognise.',
            'description': 'Optional. Describe the purpose or goals of this group.',
        }


class GroupTaskForm(forms.ModelForm):
    """Used when CREATING a new task. assigned_to queryset set dynamically in the view."""

    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=False,
        help_text="Optional. Set a deadline to keep the team accountable.",
    )

    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.MultipleHiddenInput(),
        help_text="Select one or more group members to assign this task to.",
    )

    class Meta:
        model = GroupTask
        fields = ['title', 'description', 'attachment', 'assigned_to', 'priority', 'deadline', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Compile research sources, Draft introduction…',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'What exactly needs to be done? Be specific so the assignee is clear.',
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'title': 'A clear, action-oriented task title.',
            'description': 'Optional. Provide details, context, or links.',
            'attachment': 'Optional. Upload an image, doc, or file for reference.',
            'priority': 'Task urgency level.',
            'status': 'Current progress status for this task.',
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow assignment to any user in the system (new assignees are auto-added to the group in views.py)
        self.fields['assigned_to'].queryset = User.objects.all()


class EditGroupTaskForm(GroupTaskForm):
    """Identical to GroupTaskForm — kept separate for clarity in views."""
    pass


class AddMemberForm(forms.Form):
    """Simple form to add a user to a group by username."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by username…',
            'autocomplete': 'off',
            'id': 'add-member-input',
        }),
    )
