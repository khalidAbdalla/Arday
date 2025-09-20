from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.http import Http404
from django.core.exceptions import PermissionDenied
from datetime import timedelta
from .models import User, School, Class, StudentEnrollment, Grade, Announcement

# Create your views here.

# ==================== SCHOOL-BASED LOGIN VIEWS ====================

def student_login(request, school_slug):
    """Student login for specific school"""
    school = get_object_or_404(School, slug=school_slug)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                # Verify user is a student of this school
                if user.role == 'student' and user.school == school:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('student_dashboard', school_slug=school_slug)
                else:
                    messages.error(request, 'Access denied. You are not authorized for this school.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'school': school,
        'role': 'Student',
        'login_url': 'student_login',
        'dashboard_url': 'student_dashboard'
    }
    return render(request, 'accounts/login/student_login.html', context)

def teacher_login(request, school_slug):
    """Teacher login for specific school"""
    school = get_object_or_404(School, slug=school_slug)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                # Verify user is a teacher of this school
                if user.role == 'teacher' and user.school == school:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('teacher_dashboard', school_slug=school_slug)
                else:
                    messages.error(request, 'Access denied. You are not authorized for this school.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'school': school,
        'role': 'Teacher',
        'login_url': 'teacher_login',
        'dashboard_url': 'teacher_dashboard'
    }
    return render(request, 'accounts/login/teacher_login.html', context)

def school_admin_login(request, school_slug):
    """School admin login for specific school"""
    school = get_object_or_404(School, slug=school_slug)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                # Verify user is a school admin of this school
                if user.role == 'schooladmin' and user.school == school:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('school_admin_dashboard', school_slug=school_slug)
                else:
                    messages.error(request, 'Access denied. You are not authorized for this school.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'school': school,
        'role': 'School Administrator',
        'login_url': 'school_admin_login',
        'dashboard_url': 'school_admin_dashboard'
    }
    return render(request, 'accounts/login/school_admin_login.html', context)

def super_admin_login(request):
    """Super admin login (global access)"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                # Verify user is a super admin
                if user.role == 'superadmin':
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('super_admin_dashboard')
                else:
                    messages.error(request, 'Access denied. Super Admin access required.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'role': 'Super Administrator',
        'login_url': 'super_admin_login',
        'dashboard_url': 'super_admin_dashboard'
    }
    return render(request, 'accounts/login/super_admin_login.html', context)

# ==================== SECURITY DECORATORS ====================

def require_school_access(school_slug_param='school_slug'):
    """Decorator to ensure user has access to the specified school"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            school_slug = kwargs.get(school_slug_param)
            school = get_object_or_404(School, slug=school_slug)
            
            if not request.user.is_authenticated:
                return redirect('student_login', school_slug=school_slug)
            
            # Super admin can access any school
            if request.user.role == 'superadmin':
                return view_func(request, *args, **kwargs)
            
            # Check if user belongs to this school
            if request.user.school != school:
                raise PermissionDenied("You don't have access to this school.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role):
    """Decorator to ensure user has the required role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('super_admin_login')
            
            if request.user.role != required_role:
                raise PermissionDenied(f"Access denied. {required_role.title()} role required.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# ==================== LEGACY REDIRECT VIEW ====================

@login_required
def dashboard_redirect(request):
    """Redirect users to their role-specific dashboard"""
    user = request.user
    
    if user.is_superadmin():
        return redirect('super_admin_dashboard')
    elif user.is_schooladmin():
        return redirect('school_admin_dashboard')
    elif user.is_teacher():
        return redirect('teacher_dashboard')
    elif user.is_student():
        return redirect('student_dashboard')
    else:
        messages.error(request, 'Invalid user role.')
        return redirect('admin:index')

# ==================== SCHOOL-BASED DASHBOARD VIEWS ====================

@login_required
@require_role('superadmin')
def super_admin_dashboard(request):
    """Super Admin Dashboard - Shows all data across all schools"""
    
    # Get all data across all schools
    total_schools = School.objects.count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_students = User.objects.filter(role='student').count()
    total_classes = Class.objects.count()
    
    # Chart data
    super_admin_count = User.objects.filter(role='superadmin').count()
    school_admin_count = User.objects.filter(role='schooladmin').count()
    
    # Recent activity
    recent_schools = School.objects.order_by('-created_at')[:5]
    recent_announcements = Announcement.objects.order_by('-created_at')[:10]
    
    # Statistics
    schools_with_most_students = School.objects.annotate(
        student_count=Count('user', filter=Q(user__role='student'))
    ).order_by('-student_count')[:5]
    
    context = {
        'total_schools': total_schools,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_classes': total_classes,
        'super_admin_count': super_admin_count,
        'school_admin_count': school_admin_count,
        'recent_schools': recent_schools,
        'recent_announcements': recent_announcements,
        'schools_with_most_students': schools_with_most_students,
    }
    
    return render(request, 'accounts/dashboards/super_admin.html', context)

@login_required
@require_school_access()
def school_admin_dashboard(request, school_slug):
    """School Admin Dashboard - Shows data for their school only"""
    school = get_object_or_404(School, slug=school_slug)
    
    # Additional security check
    if request.user.role != 'schooladmin':
        raise PermissionDenied("School Admin access required.")
    
    # Get data for this school only
    school_teachers = User.objects.filter(school=school, role='teacher')
    school_students = User.objects.filter(school=school, role='student')
    school_classes = Class.objects.filter(school=school)
    
    # Statistics
    total_teachers = school_teachers.count()
    total_students = school_students.count()
    total_classes = school_classes.count()
    
    # Recent activity for this school
    recent_announcements = Announcement.objects.filter(
        Q(school=school) | Q(school__isnull=True)
    ).order_by('-created_at')[:10]
    
    # Class statistics
    classes_with_enrollment = school_classes.annotate(
        enrollment_count=Count('studentenrollment')
    ).order_by('-enrollment_count')[:5]
    
    context = {
        'school': school,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_classes': total_classes,
        'school_teachers': school_teachers[:10],
        'school_students': school_students[:10],
        'school_classes': school_classes[:10],
        'recent_announcements': recent_announcements,
        'classes_with_enrollment': classes_with_enrollment,
    }
    
    return render(request, 'accounts/dashboards/school_admin.html', context)

@login_required
@require_school_access()
def teacher_dashboard(request, school_slug):
    """Teacher Dashboard - Shows only their classes and students"""
    school = get_object_or_404(School, slug=school_slug)
    
    # Additional security check
    if request.user.role != 'teacher':
        raise PermissionDenied("Teacher access required.")
    
    # Get teacher's classes
    teacher_classes = Class.objects.filter(teacher=request.user)
    
    # Get students enrolled in teacher's classes
    student_enrollments = StudentEnrollment.objects.filter(
        class_enrolled__in=teacher_classes
    ).select_related('student', 'class_enrolled')
    
    # Get recent grades for teacher's classes
    recent_grades = Grade.objects.filter(
        class_enrolled__in=teacher_classes
    ).order_by('-created_at')[:10]
    
    # Statistics
    total_classes = teacher_classes.count()
    total_students = student_enrollments.values('student').distinct().count()
    
    # Class performance (average grades)
    class_performance = []
    for class_obj in teacher_classes:
        avg_grade = Grade.objects.filter(
            class_enrolled=class_obj
        ).aggregate(avg_grade=Avg('grade'))['avg_grade'] or 0
        
        class_performance.append({
            'class': class_obj,
            'avg_grade': round(avg_grade, 2),
            'student_count': StudentEnrollment.objects.filter(class_enrolled=class_obj).count()
        })
    
    # Recent announcements for teacher's classes
    recent_announcements = Announcement.objects.filter(
        Q(class_target__in=teacher_classes) | Q(school=school)
    ).order_by('-created_at')[:5]
    
    context = {
        'teacher_classes': teacher_classes,
        'student_enrollments': student_enrollments[:20],
        'recent_grades': recent_grades,
        'total_classes': total_classes,
        'total_students': total_students,
        'class_performance': class_performance,
        'recent_announcements': recent_announcements,
    }
    
    return render(request, 'accounts/dashboards/teacher.html', context)

@login_required
@require_school_access()
def student_dashboard(request, school_slug):
    """Student Dashboard - Shows only their own data"""
    school = get_object_or_404(School, slug=school_slug)
    
    # Additional security check
    if request.user.role != 'student':
        raise PermissionDenied("Student access required.")
    
    # Get student's enrollments
    student_enrollments = StudentEnrollment.objects.filter(
        student=request.user
    ).select_related('class_enrolled', 'class_enrolled__teacher')
    
    # Get student's grades
    student_grades = Grade.objects.filter(
        student=request.user
    ).order_by('-created_at')
    
    # Calculate GPA
    if student_grades.exists():
        gpa = student_grades.aggregate(avg_grade=Avg('grade'))['avg_grade']
        gpa = round(gpa, 2) if gpa else 0
    else:
        gpa = 0
    
    # Recent grades
    recent_grades = student_grades[:10]
    
    # Grades by class
    grades_by_class = {}
    for enrollment in student_enrollments:
        class_grades = student_grades.filter(class_enrolled=enrollment.class_enrolled)
        if class_grades.exists():
            class_avg = class_grades.aggregate(avg_grade=Avg('grade'))['avg_grade']
            grades_by_class[enrollment.class_enrolled] = {
                'grades': class_grades[:5],
                'average': round(class_avg, 2) if class_avg else 0
            }
    
    # Recent announcements for student's classes
    student_classes = [enrollment.class_enrolled for enrollment in student_enrollments]
    recent_announcements = Announcement.objects.filter(
        Q(class_target__in=student_classes) | Q(school=school)
    ).order_by('-created_at')[:5]
    
    context = {
        'student_enrollments': student_enrollments,
        'student_grades': student_grades,
        'recent_grades': recent_grades,
        'gpa': gpa,
        'grades_by_class': grades_by_class,
        'recent_announcements': recent_announcements,
        'total_classes': student_enrollments.count(),
    }
    
    return render(request, 'accounts/dashboards/student.html', context)
