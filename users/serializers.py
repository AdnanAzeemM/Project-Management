from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from project.models import Project
from django.contrib.auth.models import Group, Permission
from users.models import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email

        return token


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    projects_detail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'projects': {'required': False}
        }

    def get_projects_detail(self, obj):
        return [project.project_name for project in obj.projects.all()]

