import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import User, AuthToken
from .forms import RegisterForm, LoginForm, ProfileForm, ForgotPasswordForm, ResetPasswordForm

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _build_link(request, path: str) -> str:
    """Build an absolute URL using FRONTEND_URL from settings."""
    base = getattr(settings, 'FRONTEND_URL', 'http://127.0.0.1:8000').rstrip('/')
    return f"{base}{path}"


def _send_verification_email(request, user):
    lifetime_h = getattr(settings, 'EMAIL_VERIFICATION_TIMEOUT_HOURS', 24)
    raw = AuthToken.generate(user, 'verify', lifetime_h * 60)
    link = _build_link(request, f"/accounts/verify-email/{raw}/")

    subject = "✅ Verify your AcadConnect account"
    html_body = render_to_string('emails/verify_email.html', {
        'user': user, 'link': link, 'hours': lifetime_h,
    })
    text_body = (
        f"Hi {user.first_name or user.username},\n\n"
        f"Please verify your AcadConnect account by visiting:\n{link}\n\n"
        f"This link expires in {lifetime_h} hours."
    )
    try:
        send_mail(subject, text_body, settings.DEFAULT_FROM_EMAIL,
                  [user.email], html_message=html_body, fail_silently=False)
    except Exception as exc:
        logger.error("Failed to send verification email to %s: %s", user.email, exc)


def _send_reset_email(request, user):
    lifetime_m = getattr(settings, 'PASSWORD_RESET_TIMEOUT_MINUTES', 30)
    raw = AuthToken.generate(user, 'reset', lifetime_m)
    link = _build_link(request, f"/accounts/reset-password/{raw}/")

    subject = "🔑 Reset your AcadConnect password"
    html_body = render_to_string('emails/reset_password.html', {
        'user': user, 'link': link, 'minutes': lifetime_m,
    })
    text_body = (
        f"Hi {user.first_name or user.username},\n\n"
        f"Reset your password here:\n{link}\n\n"
        f"This link expires in {lifetime_m} minutes. If you didn't request this, ignore this email."
    )
    try:
        send_mail(subject, text_body, settings.DEFAULT_FROM_EMAIL,
                  [user.email], html_message=html_body, fail_silently=False)
    except Exception as exc:
        logger.error("Failed to send reset email to %s: %s", user.email, exc)


def _is_resend_throttled(request, key: str) -> bool:
    """Return True if the user has resent within RESEND_COOLDOWN_SECONDS."""
    cooldown = getattr(settings, 'RESEND_COOLDOWN_SECONDS', 60)
    last_sent = request.session.get(key)
    if last_sent:
        elapsed = (timezone.now().timestamp() - last_sent)
        if elapsed < cooldown:
            return True
    return False


def _mark_resend(request, key: str):
    request.session[key] = timezone.now().timestamp()


# ──────────────────────────────────────────────────────────────────────────────
# Landing
# ──────────────────────────────────────────────────────────────────────────────
def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'accounts/landing.html')


# ──────────────────────────────────────────────────────────────────────────────
# Register
# ──────────────────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.is_active = True          # account exists but email unverified
            user.save()
            _send_verification_email(request, user)
            _mark_resend(request, f'verify_sent_{user.email}')
            request.session['pending_email'] = user.email
            return redirect('accounts:email_sent')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# ──────────────────────────────────────────────────────────────────────────────
# Email Sent notice
# ──────────────────────────────────────────────────────────────────────────────
def email_sent_view(request):
    email = request.session.get('pending_email', '')
    steps = [
        (1, 'Open the email from AcadConnect in your inbox.'),
        (2, 'Click the "Verify My Email" button in the email.'),
        (3, "You'll be redirected back here to log in."),
    ]
    return render(request, 'accounts/email_sent.html', {'email': email, 'steps': steps})


# ──────────────────────────────────────────────────────────────────────────────
# Verify Email
# ──────────────────────────────────────────────────────────────────────────────
def verify_email_view(request, token):
    token_obj = AuthToken.validate(token, 'verify')
    if token_obj is None:
        return render(request, 'accounts/verify_invalid.html', status=400)

    user = token_obj.user
    token_obj.used = True
    token_obj.save(update_fields=['used'])

    user.is_email_verified = True
    user.save(update_fields=['is_email_verified'])

    # Clean up pending session
    request.session.pop('pending_email', None)

    return render(request, 'accounts/verify_success.html', {'user': user})


# ──────────────────────────────────────────────────────────────────────────────
# Resend Verification
# ──────────────────────────────────────────────────────────────────────────────
def resend_verification_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        throttle_key = f'verify_sent_{email}'
        try:
            user = User.objects.filter(email=email, is_email_verified=False).order_by('-date_joined').first()
            if not user:
                raise User.DoesNotExist
        except User.DoesNotExist:
            # Silently succeed — don't reveal whether email exists
            messages.success(request, "If that email is on file, a new verification link has been sent.")
            return redirect('accounts:login')

        if _is_resend_throttled(request, throttle_key):
            cooldown = getattr(settings, 'RESEND_COOLDOWN_SECONDS', 60)
            messages.warning(request, f"Please wait {cooldown} seconds before requesting another link.")
        else:
            _send_verification_email(request, user)
            _mark_resend(request, throttle_key)
            request.session['pending_email'] = email
            messages.success(request, "A new verification link has been sent to your email.")
            return redirect('accounts:email_sent')

    return redirect('accounts:login')


# ──────────────────────────────────────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    unverified_email = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                if not user.is_email_verified:
                    unverified_email = user.email
                    messages.warning(
                        request,
                        "Please verify your email before logging in. Check your inbox or resend below."
                    )
                else:
                    login(request, user)
                    next_url = request.GET.get('next', 'dashboard:home')
                    return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'unverified_email': unverified_email,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Logout
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out. See you soon! 👋")
    return redirect('accounts:login')


# ──────────────────────────────────────────────────────────────────────────────
# Forgot Password
# ──────────────────────────────────────────────────────────────────────────────
def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()
            throttle_key = f'reset_sent_{email}'

            # Use filter().first() to safely handle duplicate emails (anti-enumeration + crash prevention)
            user = User.objects.filter(email=email).order_by('-date_joined').first()
            if user:
                if _is_resend_throttled(request, throttle_key):
                    cooldown = getattr(settings, 'RESEND_COOLDOWN_SECONDS', 60)
                    messages.warning(request, f"Please wait {cooldown} seconds before requesting another reset.")
                else:
                    _send_reset_email(request, user)
                    _mark_resend(request, throttle_key)
            # If user not found: silently succeed (anti-enumeration)

            # Always redirect to the same confirmation page
            return render(request, 'accounts/forgot_password.html', {
                'form': form, 'email_sent': True, 'email': email,
            })

    return render(request, 'accounts/forgot_password.html', {'form': form, 'email_sent': False})


# ──────────────────────────────────────────────────────────────────────────────
# Reset Password
# ──────────────────────────────────────────────────────────────────────────────
def reset_password_view(request, token):
    token_obj = AuthToken.validate(token, 'reset')
    if token_obj is None:
        return render(request, 'accounts/reset_invalid.html', status=400)

    user = token_obj.user
    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['password1']
            user.set_password(new_password)
            user.save()

            # Invalidate the token
            token_obj.used = True
            token_obj.save(update_fields=['used'])

            # Also invalidate any other reset tokens for this user
            AuthToken.objects.filter(user=user, token_type='reset', used=False).update(used=True)

            messages.success(request, "Your password has been reset successfully. Please log in.")
            return redirect('accounts:login')

    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})


# ──────────────────────────────────────────────────────────────────────────────
# Profile
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


# ──────────────────────────────────────────────────────────────────────────────
# Toggle dark mode
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def toggle_dark_mode(request):
    user = request.user
    user.dark_mode = not user.dark_mode
    user.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:home'))
