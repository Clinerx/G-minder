from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings  # for referencing AUTH_USER_MODEL
from django.utils import timezone


class MentalHealthEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    mood = models.CharField(max_length=20)
    mood_rating = models.PositiveIntegerField()
    thoughts = models.TextField()
    reflection = models.TextField(blank=True)
    gratitude = models.TextField(blank=True)
    goal = models.CharField(max_length=255, blank=True)
    self_care = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.date}"
    
# Task model linked to CustomUser via settings.AUTH_USER_MODEL
class Task(models.Model):
    # Enum-style status field
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        IN_PROGRESS = 'In Progress', 'In Progress'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING  # Default to Pending when a task is created
    )

    @property
    def is_overdue(self):
        if self.due_date and self.status != self.Status.COMPLETED:
            now = timezone.now()
            return now > self.due_date
        return False

    def __str__(self):
        return self.name
    

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=email, username=username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


# Custom User Model
class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
