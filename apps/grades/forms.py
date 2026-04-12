from django import forms
from .models import Course, Assessment


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'credit_hours', 'professor', 'semester', 'color']
        widgets = {'color': forms.TextInput(attrs={'type': 'color'})}


class AssessmentForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Assessment
        fields = ['name', 'assessment_type', 'score', 'max_score', 'weight', 'date']
