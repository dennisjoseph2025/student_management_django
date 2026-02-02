from django.db import models

class Department(models.Model):
    dept_name = models.CharField(max_length=20)
    dept_description = models.TextField()

    def __str__(self):
        return self.dept_name

class AddOnCourse(models.Model):
    course_id = models.CharField(max_length=20, unique=True, null=True, blank=True) 
    course_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    course_description = models.TextField()
    course_price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.course_id or 'No ID'} - {self.course_name}"
    @property
    def formatted_price(self):
        return f"₹{self.course_price:,}"