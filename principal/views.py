from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from student.models import Student, StudentCourse
from .models import Department, AddOnCourse
from .form import AddOnCourseForm  

@login_required
def principal_dashboard(request):
    # Handle form submissions for approvals and deletions
    if request.method == 'POST':
        action = request.POST.get('action')
        approval_id = request.POST.get('approval_id')
        
        # Process course approval or rejection
        if action in ['approve_course', 'reject_course'] and approval_id:
            try:
                approval = StudentCourse.objects.get(id=approval_id)
                if action == 'approve_course':
                    approval.status = 'APPROVED'
                    approval.approved_at = timezone.now()
                    messages.success(request, f'Course "{approval.course.course_name}" approved for {approval.student.first_name}')
                else:
                    approval.status = 'REJECTED'
                    messages.success(request, f'Course "{approval.course.course_name}" rejected for {approval.student.first_name}')
                approval.save()
            except StudentCourse.DoesNotExist:
                messages.error(request, 'Approval request not found.')
        
        # Process course deletion
        elif action == 'delete_course':
            course_id = request.POST.get('course_id')
            try:
                course = AddOnCourse.objects.get(id=course_id)
                course_name = course.course_name
                course.delete()
                messages.success(request, f'Course "{course_name}" deleted successfully!')
            except AddOnCourse.DoesNotExist:
                messages.error(request, 'Course not found.')
        
        return redirect('principal_dashboard')
    
    # Calculate dashboard statistics
    total_students = Student.objects.filter(role='STUDENT').count()
    total_departments = Department.objects.count()
    total_courses = AddOnCourse.objects.count()
    pending_requests = StudentCourse.objects.filter(status='PENDING').count()
    
    total_revenue = StudentCourse.objects.filter(status='APPROVED').aggregate(
        total=Sum('course__course_price')
    )['total'] or 0
    
    # Get recent student registrations
    recent_students = Student.objects.filter(
        role='STUDENT'
    ).select_related('std_dept').order_by('-date_joined')[:5]
    
    # Get all pending approvals
    pending_approvals = StudentCourse.objects.filter(
        status='PENDING'
    ).select_related('student', 'course', 'course__department', 'student__std_dept').order_by('-purchased_at')
    
    # Prepare department data
    departments_with_courses = []
    departments = Department.objects.all()
    
    for dept in departments:
        courses = AddOnCourse.objects.filter(department=dept)
        departments_with_courses.append({
            'id': dept.id,
            'dept_name': dept.dept_name,
            'dept_description': dept.dept_description,
            'course_count': courses.count(),
        })
    
    context = {
        'total_students': total_students,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'active_courses': total_courses,
        'pending_requests': pending_requests,
        'total_revenue': total_revenue,
        'recent_students': recent_students,
        'pending_approvals': pending_approvals,
        'departments_with_courses': departments_with_courses,
    }
    
    return render(request, 'principal_dashboard.html', context)
@login_required
def course_list(request):
    # Handle course deletion
    if request.method == 'POST' and request.POST.get('action') == 'delete_course':
        course_id = request.POST.get('course_id')
        try:
            course = AddOnCourse.objects.get(id=course_id)
            course_name = course.course_name
            course.delete()
            messages.success(request, f'Course "{course_name}" deleted successfully!')
        except AddOnCourse.DoesNotExist:
            messages.error(request, 'Course not found.')
        return redirect('course_list')
    
    # Get all departments for filter dropdown
    departments = Department.objects.all()
    
    # Get filter parameters
    selected_department = request.GET.get('department')
    search_query = request.GET.get('search', '')
    
    # Start with all courses
    courses = AddOnCourse.objects.all().select_related('department').order_by('course_name')
    
    # Apply filters
    if selected_department:
        courses = courses.filter(department_id=selected_department)
    
    if search_query:
        courses = courses.filter(
            Q(course_name__icontains=search_query) |
            Q(course_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(courses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': page_obj,
        'departments': departments,
        'selected_department': selected_department,
        'search_query': search_query,
        'total_courses': paginator.count,
    }
    
    return render(request, 'principal_course_list.html', context)
@login_required

def students_list(request):  
    # Get all students
    students = Student.objects.filter(role='STUDENT').select_related('std_dept').order_by('-date_joined')
    
    # Apply search
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(std_reg_no__icontains=search_query)
        )
    
    context = {
        'students': students,
        'search_query': search_query,
        'total_students': students.count(),
    }
    
    return render(request, 'principal_students_list.html', context)


@login_required
def Add_course(request):   
    # Check if departments exist
    departments = Department.objects.all()
    if not departments.exists():
        messages.warning(request, 'Please create a department first before adding courses.')
        return redirect('principal_dashboard')
    
    if request.method == 'POST':
        form = AddOnCourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.course_name}" added successfully!')
            return redirect('principal_dashboard')
    else:
        form = AddOnCourseForm()
    
    context = {
        'form': form,
        'departments': departments, 
    }
    
    return render(request, 'add_course.html', context)

@login_required
def student_view(request, student_id):  
    # Handle course approval/rejection
    if request.method == 'POST':
        action = request.POST.get('action')
        purchase_id = request.POST.get('purchase_id')
        
        if action in ['approve_purchase', 'reject_purchase'] and purchase_id:
            try:
                purchase = StudentCourse.objects.get(id=purchase_id)
                if action == 'approve_purchase':
                    purchase.status = 'APPROVED'
                    purchase.approved_at = timezone.now()
                    messages.success(request, f'Course "{purchase.course.course_name}" approved for {purchase.student.first_name}')
                else:
                    purchase.status = 'REJECTED'
                    messages.success(request, f'Course "{purchase.course.course_name}" rejected for {purchase.student.first_name}')
                purchase.save()
            except StudentCourse.DoesNotExist:
                messages.error(request, 'Course purchase not found.')
        
        return redirect('student_view', student_id=student_id)
    
    # Get student by ID
    student = get_object_or_404(Student, id=student_id, role='STUDENT')
    
    # Get all courses purchased by this student
    all_courses = StudentCourse.objects.filter(
        student=student
    ).select_related('course', 'course__department').order_by('-purchased_at')
    
    # Separate courses by status
    approved_courses = all_courses.filter(status='APPROVED')
    pending_courses = all_courses.filter(status='PENDING')
    rejected_courses = all_courses.filter(status='REJECTED')
    
    # Calculate total spent
    total_spent = sum(purchase.course.course_price for purchase in approved_courses)
    
    context = {
        'student': student,
        'student_courses': all_courses,
        'approved_courses': approved_courses,
        'pending_courses': pending_courses,
        'rejected_courses': rejected_courses,
        'total_spent': total_spent,
        'approved_count': approved_courses.count(),
        'pending_count': pending_courses.count(),
        'rejected_count': rejected_courses.count(),
    }
    
    return render(request, 'principal_student_view.html', context)