from rest_framework import serializers
from project.models import Project, Task

from users.models import User


class ProjectSerializer(serializers.ModelSerializer):
    users = serializers.StringRelatedField(many=True, source='user_project')

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'users']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'project']
