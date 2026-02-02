from django.db import models
from django.contrib.auth.models import AbstractUser
from principal.models import Department
from datetime import date

class Student(AbstractUser):
    # Role choices
    USER_ROLES = (
        ('STUDENT', 'Student'),
        ('PRINCIPAL', 'Principal'),
    )
    
    # Custom fields
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default='STUDENT'
    )
    std_age = models.IntegerField(null=True, blank=True)

    # Updated to use Cloudinary
    std_pic = models.ImageField(upload_to="student_pic", null=True, blank=True)

    std_reg_no = models.CharField(max_length=12, unique=True)
    std_dept = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    std_year_of_admission = models.IntegerField(default=date.today().year)
    std_phone_no = models.CharField(max_length=10, null=True, blank=True)
    purchased_courses = models.ManyToManyField(
        'principal.AddOnCourse',
        blank=True,
        related_name='students',
        through='StudentCourse'
    )
    
    # Override AbstractUser fields to make them required
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True) 
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.std_reg_no} ({self.role})"


class StudentCourse(models.Model):
    """Track student course purchases with approval status"""
    PURCHASE_STATUS = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_purchases')
    course = models.ForeignKey('principal.AddOnCourse', on_delete=models.CASCADE, related_name='student_purchases')
    status = models.CharField(max_length=20, choices=PURCHASE_STATUS, default='PENDING')
    purchased_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.student.std_reg_no} - {self.course.course_name} ({self.status})"
