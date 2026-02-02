from django.urls import path
from . import views

urlpatterns = [
    path('principal-dashboard/', views.principal_dashboard, name='principal_dashboard'),
    path('add-course/', views.Add_course, name='add_course'),
    path('user/<int:student_id>/', views.student_view, name='student_view'),
    path('users-list/', views.students_list, name='students_list'),
    path('course-list/', views.course_list, name='course_list'),

]