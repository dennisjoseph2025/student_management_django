from django.contrib import admin
from .models import Student

# Register your models here.


class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'username',
        'std_age',
        'email',
        'std_reg_no',
        'std_dept',
        'std_year_of_admission',
        'std_phone_no',
        'role'
    )


admin.site.register(Student, StudentAdmin)
