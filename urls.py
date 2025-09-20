from django.urls import path, include
from . import views

# School-based URL patterns
school_patterns = [
    # Student login and dashboard
    path('', views.student_login, name='student_login'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Teacher login and dashboard
    path('teachers/', views.teacher_login, name='teacher_login'),
    path('teachers/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # School admin login and dashboard
    path('admin/', views.school_admin_login, name='school_admin_login'),
    path('admin/dashboard/', views.school_admin_dashboard, name='school_admin_dashboard'),
]

# Main URL patterns
urlpatterns = [
    # Super Admin (global access)
    path('super-admin/', views.super_admin_login, name='super_admin_login'),
    path('super-admin/dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),
    
    # School-based URLs (will be included in main project URLs)
    path('<slug:school_slug>/', include(school_patterns)),
    
    # Legacy redirects (for backward compatibility)
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('legacy/super-admin/', views.super_admin_dashboard, name='legacy_super_admin_dashboard'),
    path('legacy/school-admin/', views.school_admin_dashboard, name='legacy_school_admin_dashboard'),
    path('legacy/teacher/', views.teacher_dashboard, name='legacy_teacher_dashboard'),
    path('legacy/student/', views.student_dashboard, name='legacy_student_dashboard'),
]