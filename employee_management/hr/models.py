from datetime import timedelta, timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Custom user model
class CustomUser(AbstractUser):
    username = None
    ROLE_CHOICES = [
        ('HR', 'HR'),
        ('Employee', 'Employee'),
        ('ProjectManager', 'ProjectManager'),
        ('Intern', 'Intern'),
        ('ContractEmployee', 'ContractEmployee'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    pan_no = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    contact_no = models.CharField(max_length=100, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=100, blank=True, null=True)
    account_no = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    ROLE_CHOICES = [
        ("married", "married"),
        ('unmarried', 'unmarried'),
    ]
    marital_status = models.CharField(max_length=40, choices=ROLE_CHOICES, default="unmarried")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_max_leaves(self):
        if self.role == 'Intern' or self.role == 'ContractEmployee':
            return 1
        elif self.role == 'Employee':
            return 2
        else:
            return 0

# Department model
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Leave model
class Leave(models.Model):
    LEAVE_TYPES = [
        ('medical', 'medical'),
        ('sick', 'sick'),
        ('casual', 'casual'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f'{self.employee.email} - {self.leave_type}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.apply_leave_policy()
        super().save(*args, **kwargs)

    def apply_leave_policy(self):
        user = self.employee
        current_date = timezone.now()
        first_day_of_month = current_date.replace(day=1)
        last_day_of_month = current_date.replace(day=28) + timedelta(days=4)
        last_day_of_month = last_day_of_month - timedelta(days=last_day_of_month.day)
        
        # Count leaves taken this month
        leaves_this_month = Leave.objects.filter(
            employee=self.employee,
            start_date__range=(first_day_of_month, last_day_of_month)
        ).count()

        max_leaves = user.get_max_leaves()

        if leaves_this_month >= max_leaves:
            raise ValueError("You have exceeded the number of leaves you can take this month.")

# Project model
class Project(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    project_manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='projects_managed')

    def __str__(self):
        return self.name

# Team model
class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='teams')
    members = models.ManyToManyField(CustomUser, related_name='teams')

    def __str__(self):
        return f'{self.project.name} Team'

# Attendance model
class Attendance(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.employee.email} - {self.date}'

# OTP model for invitation
class OTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.email} - {self.otp}'
