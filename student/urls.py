from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/',views.login, name='login' ),
    path('logout/', views.logout_view, name='logout'),
    path('registration/',views.registration, name='registration' ),
    path('student-purchase-course/', views.purchase_course, name='purchase_course'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
]  