from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('schooladmin', 'School Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    school = models.ForeignKey('School', on_delete=models.CASCADE, null=True, blank=True)

    def is_superadmin(self):
        return self.role == 'superadmin'

    def is_schooladmin(self):
        return self.role == 'schooladmin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

class School(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True, help_text="URL-friendly name (e.g., 'arday-high-school')")
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    # logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)  # Requires Pillow
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-').replace('&', 'and')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/{self.slug}/'

class Class(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    subject = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class StudentEnrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'class_enrolled']

    def __str__(self):
        return f"{self.student.username} in {self.class_enrolled.name}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE)
    assignment_name = models.CharField(max_length=200)
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    max_grade = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.assignment_name}: {self.grade}/{self.max_grade}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    class_target = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
