from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import StudentCourse
from .form import StudentForm, StudentProfileForm, StudentProfilePictureForm
from principal.models import AddOnCourse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings


# Handle landing page request
def landing(request):
    return render(request, "landing.html")


# Handle user login authentication
def login(request):
    # Process POST request for login form submission
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Validate form inputs are not empty
        if not username or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, "login.html")

        # Authenticate user with Django's auth system
        user = authenticate(request, username=username, password=password)

        # If authentication successful, log user in
        if user is not None:
            auth_login(request, user)

            # Redirect based on user role
            if user.role == "STUDENT":
                return redirect("student_dashboard")
            elif user.role == "PRINCIPAL":
                return redirect("principal_dashboard")
            else:
                messages.error(request, "Invalid user role.")
                return render(request, "login.html")
        else:
            # Check if user exists to show specific error message
            user_exists = StudentCourse.objects.filter(student__email=username).exists()
            if user_exists:
                messages.error(request, "Invalid password. Please try again.")
            else:
                messages.error(
                    request, "No account found with this email. Please register first."
                )
            return render(request, "login.html")

    # Render login page for GET requests
    return render(request, "login.html")


# Handle new student registration
def registration(request):
    # Process POST request for registration form
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)

        # Validate and save form data
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data["email"]
            user.role = "STUDENT"
            user.save()
            try:
                # Send welcome email to new user
                send_welcome_email(user)
                messages.success(
                    request,
                    "Registration successful! A welcome email has been sent to your inbox.",
                )
            except Exception as e:
                messages.success(
                    request,
                    f"Registration successful! (Note: Welcome email could not be sent)",
                )
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Create empty form for GET requests
        form = StudentForm()
    return render(request, "registration.html", {"form": form})


# Send welcome email to newly registered users
def send_welcome_email(user):
    #Send simple welcome email
    subject = f"Welcome to Student Management System, {user.first_name}!"

    message = f"""
Welcome to Student Management System!

Your account has been successfully created.

Account Details:
• Name: {user.first_name} {user.last_name}
• Email: {user.email}
• Registration No: {user.std_reg_no}
• Username/Email: {user.email}
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


# Handle course purchase requests (requires login)
@login_required
def purchase_course(request):
    # Process POST request for course selection
    if request.method == "POST":
        selected_course_ids = request.POST.getlist("selected_courses")
        if selected_course_ids:
            # Get selected course objects from database
            courses = AddOnCourse.objects.filter(id__in=selected_course_ids)
            created_count = 0

            # Create course enrollment for each selected course
            for course in courses:
                created = StudentCourse.objects.get_or_create(
                    student=request.user, course=course, defaults={"status": "PENDING"}
                )
                if created:
                    created_count += 1

            # Show success message with count of new requests
            if created_count > 0:
                messages.success(
                    request, f"{created_count} course(s) requested for approval!"
                )
            else:
                messages.info(request, "All selected courses were already requested.")
            return redirect("student_dashboard")
        else:
            messages.error(request, "Please select at least one course.")

    # For GET requests, show available courses
    all_courses = AddOnCourse.objects.all()
    student_courses = StudentCourse.objects.filter(student=request.user)
    purchased_course_ids = list(student_courses.values_list("course_id", flat=True))
    paginator = Paginator(all_courses, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # Render purchase page with course data
    return render(
        request,
        "purchase_course.html",
        {
            "courses": page_obj,
            "count": all_courses.count(),
            "purchased_course_ids": purchased_course_ids,
            "total_courses": paginator.count,
            "student_courses": {sc.course_id: sc.status for sc in student_courses},
        },
    )


# Handle student profile management (requires login)
@login_required
def student_profile(request):
    # Process POST request for profile updates
    if request.method == "POST":
        update_type = request.POST.get("update_type", "")
        
        # Handle profile picture update separately
        if update_type == "profile_pic":
            form = StudentProfilePictureForm(request.POST, request.FILES)
            if form.is_valid():
                std_pic = form.cleaned_data['std_pic']
                
                # Delete old picture if exists
                if request.user.std_pic:
                    request.user.std_pic.delete(save=False)
                
                # Save new picture
                request.user.std_pic = std_pic
                request.user.save()
                
                messages.success(request, "Profile picture updated successfully!")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
        else:
            # Handle general profile information update
            form = StudentProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile information updated successfully!")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")

        return redirect("student_profile")

    # For GET requests, show profile page with forms
    profile_form = StudentProfileForm(instance=request.user)
    profile_pic_form = StudentProfilePictureForm()
    
    context = {
        'profile_form': profile_form,
        'profile_pic_form': profile_pic_form,
    }
    
    return render(request, "student_profile.html", context)


# Handle student dashboard display (requires login)
@login_required
def student_dashboard(request):
    # Process POST request for course removal
    if request.method == "POST" and request.POST.get("action") == "remove_course":
        student_course_id = request.POST.get("student_course_id")
        try:
            # Find and remove the enrolled course
            student_course = StudentCourse.objects.get(
                id=student_course_id, student=request.user
            )
            course_name = student_course.course.course_name
            student_course.delete()
            messages.success(request, f'Course "{course_name}" removed successfully!')
        except StudentCourse.DoesNotExist:
            messages.error(
                request, "Course not found or you do not have permission to remove it."
            )
        except Exception as e:
            messages.error(request, f"Error removing course: {str(e)}")
        return redirect("student_dashboard")

    # Get approved courses for display
    approved_purchases = StudentCourse.objects.filter(
        student=request.user, status="APPROVED"
    ).select_related("course", "course__department")

    # Get pending courses for status display
    pending_purchases = StudentCourse.objects.filter(
        student=request.user, status="PENDING"
    ).select_related("course", "course__department")

    # Get rejected courses for status display
    rejected_purchases = StudentCourse.objects.filter(
        student=request.user, status="REJECTED"
    ).select_related("course", "course__department")

    # Calculate dashboard statistics
    total_courses_bought = approved_purchases.count()
    total_amount_spent = (
        sum(sc.course.course_price for sc in approved_purchases)
        if approved_purchases.exists()
        else 0
    )

    # Prepare context data for template
    context = {
        "courses": approved_purchases,
        "approved_courses": approved_purchases.count(),
        "pending_courses": pending_purchases.count(),
        "rejected_courses": rejected_purchases.count(),
        "pending_purchases": pending_purchases,
        "rejected_purchases": rejected_purchases,
        "total_courses_bought": total_courses_bought,
        "total_amount_spent": total_amount_spent,
        "in_progress_courses": 0,
        "completed_courses": 0,
        
        'a':request.user.is_authenticated
    }

    return render(request, "student_dashboard.html", context)


# Handle user logout
def logout_view(request):
    auth_logout(request)
    return redirect("login")