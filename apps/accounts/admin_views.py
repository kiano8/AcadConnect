import functools
import logging

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .models import AuthToken, User
from .forms import AdminUserEditForm
from . import views as account_views

logger = logging.getLogger(__name__)

# Session key used to flag an active admin panel session
ADMIN_SESSION_KEY = '_admin_panel_auth'


# ──────────────────────────────────────────────────────────────────────────────
# Access control decorator
# ──────────────────────────────────────────────────────────────────────────────
def admin_required(view_func):
    """
    Allow access only when:
      1. The user is authenticated (regular Django session).
      2. The user's role is 'admin'.
      3. The user has explicitly logged in via the admin panel login
         (session flag ADMIN_SESSION_KEY is True).
    All three conditions must hold simultaneously.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Must be logged in
        if not request.user.is_authenticated:
            return redirect('admin_panel:login')
        # Must have admin role
        if request.user.role != 'admin':
            messages.error(request, "Admin access only.")
            return redirect('admin_panel:login')
        # Must have authenticated through the admin panel login
        if not request.session.get(ADMIN_SESSION_KEY):
            messages.warning(request, "Please sign in via the Admin Panel.")
            return redirect('admin_panel:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ──────────────────────────────────────────────────────────────────────────────
# Admin Login
# ──────────────────────────────────────────────────────────────────────────────
def admin_login_view(request):
    # Already in an active admin session → skip login
    if (request.user.is_authenticated
            and request.user.role == 'admin'
            and request.session.get(ADMIN_SESSION_KEY)):
        return redirect('admin_panel:user_list')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
        elif user.role != 'admin':
            messages.error(
                request,
                "This account does not have admin privileges."
            )
        elif not user.is_active:
            messages.error(request, "This account has been suspended.")
        else:
            # Set the admin panel session flag without disturbing the
            # existing student session (if any).
            from django.contrib.auth import login
            login(request, user)
            request.session[ADMIN_SESSION_KEY] = True
            messages.success(request, f"Welcome, {user.full_name}. You are now in the Admin Panel.")
            return redirect('admin_panel:user_list')

    return render(request, 'admin_panel/login.html')


# ──────────────────────────────────────────────────────────────────────────────
# Admin Logout
# ──────────────────────────────────────────────────────────────────────────────
def admin_logout_view(request):
    """Clear only the admin panel session flag, then redirect to admin login."""
    request.session.pop(ADMIN_SESSION_KEY, None)
    messages.info(request, "You have been signed out of the Admin Panel.")
    return redirect('admin_panel:login')


# ──────────────────────────────────────────────────────────────────────────────
# User List
# ──────────────────────────────────────────────────────────────────────────────
@admin_required
def admin_user_list(request):
    q = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all().order_by('-date_joined')

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )

    if role_filter:
        users = users.filter(role=role_filter)

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'suspended':
        users = users.filter(is_active=False)
    elif status_filter == 'unverified':
        users = users.filter(is_email_verified=False, is_active=True)

    total = User.objects.count()
    active_count = User.objects.filter(is_active=True).count()
    suspended_count = User.objects.filter(is_active=False).count()
    unverified_count = User.objects.filter(is_email_verified=False, is_active=True).count()

    return render(request, 'admin_panel/user_list.html', {
        'users': users,
        'q': q,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'total': total,
        'active_count': active_count,
        'suspended_count': suspended_count,
        'unverified_count': unverified_count,
        'role_choices': User.ROLE_CHOICES,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Edit User
# ──────────────────────────────────────────────────────────────────────────────
@admin_required
def admin_user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('admin_panel:user_list')
    else:
        form = AdminUserEditForm(instance=user)

    return render(request, 'admin_panel/user_edit.html', {
        'form': form,
        'target_user': user,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Suspend / Unsuspend
# ──────────────────────────────────────────────────────────────────────────────
@admin_required
def admin_user_toggle_suspend(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, "You cannot suspend your own account.")
        else:
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            action = "unsuspended" if user.is_active else "suspended"
            messages.success(request, f"User '{user.username}' has been {action}.")
    return redirect('admin_panel:user_list')


# ──────────────────────────────────────────────────────────────────────────────
# Delete User
# ──────────────────────────────────────────────────────────────────────────────
@admin_required
def admin_user_delete(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, "You cannot delete your own account.")
        else:
            username = user.username
            user.delete()
            messages.success(request, f"User '{username}' has been permanently deleted.")
    return redirect('admin_panel:user_list')


# ──────────────────────────────────────────────────────────────────────────────
# Approve (manually verify email)
# ──────────────────────────────────────────────────────────────────────────────
@admin_required
def admin_user_approve(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.is_email_verified = True
        user.is_active = True
        user.save(update_fields=['is_email_verified', 'is_active'])
        messages.success(request, f"Account '{user.username}' approved and email verified.")
    return redirect('admin_panel:user_list')


# ──────────────────────────────────────────────────────────────────────────────
# Reset Password (sends email)
# ──────────────────────────────────────────────────────────────────────────────
@admin_required
def admin_user_reset_password(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        try:
            account_views._send_reset_email(request, user)
            messages.success(request, f"Password reset link sent to {user.email}.")
        except Exception as exc:
            logger.error("Admin reset email failed for %s: %s", user.email, exc)
            messages.error(request, f"Failed to send reset email: {exc}")
    return redirect('admin_panel:user_list')
