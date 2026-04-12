from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


# ─── Registration ──────────────────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}))
    last_name = forms.CharField(
        max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}))
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'form-control'}))
    semester = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 2nd Year, 1st Sem', 'class': 'form-control'}))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='student',
                             widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'semester', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('password1', 'password2'):
            self.fields[name].widget.attrs.update({'class': 'form-control'})
        # Remove verbose help text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email


# ─── Login ─────────────────────────────────────────────────────────────────
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))


# ─── Profile ───────────────────────────────────────────────────────────────
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'semester',
                  'profile_photo', 'gpa_threshold', 'stress_level']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'stress_level': forms.NumberInput(attrs={'min': 1, 'max': 10, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


# ─── Forgot Password ───────────────────────────────────────────────────────
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your registered email',
            'class': 'form-control',
            'autocomplete': 'email',
        }))

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        # Silently succeed even if email not found — prevents user enumeration
        return email


# ─── Admin: Edit User ──────────────────────────────────────────────────────
class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'email',
            'role', 'semester', 'is_active', 'is_email_verified',
            'bio', 'gpa_threshold', 'stress_level',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'stress_level': forms.NumberInput(attrs={'min': 1, 'max': 10, 'class': 'form-control'}),
            'gpa_threshold': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'


# ─── Reset Password ────────────────────────────────────────────────────────
class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New password',
            'class': 'form-control',
            'autocomplete': 'new-password',
        }))
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'class': 'form-control',
            'autocomplete': 'new-password',
        }))

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2:
            if p1 != p2:
                raise ValidationError("Passwords do not match.")
            try:
                validate_password(p1)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return cleaned
