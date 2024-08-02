from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group, Permission
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_projects')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def get_projects(self, obj):
        return ''.join([p.project_name for p in obj.projects.all()])


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
