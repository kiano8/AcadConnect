import secrets
import hashlib
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    semester = models.CharField(max_length=20, blank=True)
    gpa_threshold = models.FloatField(default=2.0, help_text="Alert if GPA falls below this value")
    stress_level = models.IntegerField(default=5, help_text="1-10 scale")
    dark_mode = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    # Override AbstractUser's email to enforce uniqueness
    email = models.EmailField(unique=True, blank=False)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class AuthToken(models.Model):
    """
    Stores hashed tokens for email verification and password reset.
    The token value is NEVER stored plaintext — only its SHA-256 hash.
    """
    TYPE_CHOICES = [
        ('verify',  'Email Verification'),
        ('reset',   'Password Reset'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    token_hash = models.CharField(max_length=64, unique=True)   # SHA-256 hex = 64 chars
    token_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    expires_at = models.DateTimeField()
    used       = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.token_type} token for {self.user.username}"

    def is_valid(self):
        """Return True if token has not been used and has not expired."""
        return (not self.used) and (timezone.now() < self.expires_at)

    @classmethod
    def _hash(cls, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    @classmethod
    def generate(cls, user, token_type: str, lifetime_minutes: int) -> str:
        """
        Invalidate any existing tokens of this type for this user,
        create a new one, and return the raw (unhashed) token string.
        """
        # Invalidate old tokens of same type
        cls.objects.filter(user=user, token_type=token_type, used=False).update(used=True)

        raw = secrets.token_urlsafe(48)   # 64-char URL-safe random string
        cls.objects.create(
            user=user,
            token_hash=cls._hash(raw),
            token_type=token_type,
            expires_at=timezone.now() + timedelta(minutes=lifetime_minutes),
        )
        return raw

    @classmethod
    def validate(cls, raw_token: str, token_type: str):
        """
        Look up and return the AuthToken object if valid, else None.
        Does NOT mark as used — call .used = True; .save() after.
        """
        try:
            token_obj = cls.objects.get(
                token_hash=cls._hash(raw_token),
                token_type=token_type,
                used=False,
            )
        except cls.DoesNotExist:
            return None
        if token_obj.expires_at < timezone.now():
            token_obj.used = True
            token_obj.save(update_fields=['used'])
            return None
        return token_obj
