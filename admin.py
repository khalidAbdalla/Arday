from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, School, Class, StudentEnrollment, Grade, Announcement

class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin user list
    list_display = ('username', 'email', 'role', 'school', 'is_staff', 'is_active')
    list_filter = ('role', 'school', 'is_staff', 'is_active')

    # Organize fields when editing/adding a user
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role', 'school')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'school', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'address', 'email')
    ordering = ('name',)

class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'school', 'teacher', 'created_at')
    list_filter = ('school', 'subject', 'created_at')
    search_fields = ('name', 'subject', 'teacher__username')
    ordering = ('name',)

class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_enrolled', 'enrolled_at')
    list_filter = ('class_enrolled__school', 'enrolled_at')
    search_fields = ('student__username', 'class_enrolled__name')
    ordering = ('-enrolled_at',)

class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_enrolled', 'assignment_name', 'grade', 'max_grade', 'created_at')
    list_filter = ('class_enrolled__school', 'created_at')
    search_fields = ('student__username', 'assignment_name', 'class_enrolled__name')
    ordering = ('-created_at',)

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'class_target', 'created_by', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('title', 'content', 'created_by__username')
    ordering = ('-created_at',)

# Register all models
admin.site.register(User, CustomUserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(StudentEnrollment, StudentEnrollmentAdmin)
admin.site.register(Grade, GradeAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
