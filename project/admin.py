from django.contrib import admin
from .models import Project, Invitation


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_name',)
    search_fields = ('project_name',)
    list_filter = ('project_name',)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'email', 'message', 'accepted')



