from django.contrib import admin
from .models import Department, AddOnCourse 

# Register your models here.

class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'dept_name',
        'dept_description',
    )

class AddOnCourseAdmin(admin.ModelAdmin):
    list_display = (
        
        'course_id',
        'course_name',
        'department',
        'created_at',
    )
    
    list_filter = ('department',)
    search_fields = ('course_id', 'course_name')
    ordering = ('-created_at',)

admin.site.register(Department, DepartmentAdmin)
admin.site.register(AddOnCourse, AddOnCourseAdmin)  