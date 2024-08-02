from django.shortcuts import render

from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import UserSerializer, GroupSerializer, MyTokenObtainPairSerializer
from django.contrib.auth.models import Group
from rest_framework.views import APIView
from users.permission import IsOwner


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    required_groups = {
        'GET': ['moderators', 'members'],
        'POST': ['moderators', 'test'],
        'PUT': ['__all__'],
        'PATCH': ['__all__'],
        'DELETE': ['moderators'],
    }


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
