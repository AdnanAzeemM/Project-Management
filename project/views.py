from django.contrib.auth.models import Permission, Group
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from Projects_Management import settings
from project.models import Project, Invitation, Task
from project.permission import HasGroupPermission
from project.serializers import ProjectSerializer, TaskSerializer
from users.models import User
from rest_framework import viewsets, status
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated

from users.serializers import UserSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        'GET': ['moderators', 'manager'],
        'POST': ['moderators', 'test'],
        'PUT': ['__all__'],
        'PATCH': ['__all__'],
        'DELETE': ['moderators'],
    }


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        'GET': ['moderators', 'members'],
        'POST': ['moderators', 'test'],
        'PUT': ['__all__'],
        'PATCH': ['__all__'],
        'DELETE': ['moderators'],
    }

    @action(
        detail=True, methods=['post'],
        url_path='add-user',
        permission_classes=[IsAuthenticated, HasGroupPermission],
        required_groups={
            'GET': ['owner', ]
        }
    )
    def add_user_to_project(self, request, pk=None):
        project = self.get_object()
        email = request.data.get('email')

        if not email:
            return Response(
                {'message': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            project.user_project.add(user)
            project.save()
            return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # User not found, send invitation
            message = 'message', 'You have been invited to join the project.'
            invitation = Invitation.objects.create(
                project=project,
                email=email,
                message=message
            )
            invitation_link = request.build_absolute_uri(
                reverse('accept_invitation', kwargs={'token': invitation.token})
            )

            send_mail(
                'Project Invitation',
                f'{message}\n\nAccept the invitation by clicking the following link: {invitation_link}',
                settings.EMAIL_HOST_USER,
                [email]
            )
            return Response(
                {'message': f'User not found. Invitation sent to {email}'},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password', )
        project_name = request.data.get('project_name', )

        if not (username and email and password and project_name):
            return Response(
                {'message': 'username, password, email, project_name is required'},
                status=status.HTTP_404_NOT_FOUND
            )
        user = User(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        group_name = 'project_owner'
        group, created = Group.objects.get_or_create(name=group_name)
        permissions = Permission.objects.filter(codename__in=[
            'add_project', 'change_project', 'delete_project', 'view_project'
        ])
        group.permissions.set(permissions)
        user.groups.add(group)
        user.save()

        project = Project.objects.create(project_name=project_name)
        project.user_project.add(user)
        project.save()
        RefreshToken.for_user(user)

        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=['get'], url_path='get-project-user',
        permission_classes=[IsAuthenticated, HasGroupPermission],
        required_groups={
            'GET': ['owner',]
        }
    )
    def get_project_user(self, request):
        project_id = request.query_params.get('project_id')

        if not project_id:
            return Response(
                {'message': 'Project ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = Project.objects.get(id=project_id)
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response(
                {'message': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SendInvitationAPIView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        'GET': ['moderators', 'members'],
        'POST': ['owner', ],
        'PUT': ['__all__'],
    }

    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        user_email = request.data.get('email')
        project_id = request.data.get('project')

        if not (user_email and project_id, message):
            return Response(
                {"message": 'Project-id, user email and message required for send invitation'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response()

        invitation = Invitation.objects.create(
            project=project,
            email=user_email,
            message=message
        )
        invitation_link = request.build_absolute_uri(
            reverse('accept_invitation', kwargs={'token': invitation.token})
        )

        send_mail(
            'Project Invitation',
            f'{message}\n\nAccept the invitation by clicking the following link: {invitation_link}',
            settings.EMAIL_HOST_USER,
            [user_email]
        )

        return Response({'message': 'Invitation sent successfully'}, status=status.HTTP_200_OK)


class AcceptInvitationView(APIView):
    permission_classes = [IsAuthenticated, HasGroupPermission]
    required_groups = {
        'GET': ['moderators', 'members'],
        'POST': ['owner', ],
        'PUT': ['__all__'],
    }

    def get(self, request, token, *args, **kwargs):
        invitation = get_object_or_404(Invitation, token=token)

        if invitation.accepted:
            return Response({'message': 'Invitation already accepted'}, status=status.HTTP_400_BAD_REQUEST)

        invitation.accepted = True
        invitation.save()

        project = invitation.project
        email = invitation.email

        user, created = User.objects.get_or_create(email=email, defaults={'username': email})

        if created:
            default_password = '@new_user@'
            user.set_password(default_password)
            user.save()
            user.projects.add(project)

            send_mail(
                'Your account has been created',
                f'Your account has been created with the following credentials:\n\n'
                f'Username: {email}\nPassword: {default_password}\n\nPlease change your password after logging in.',
                settings.EMAIL_HOST_USER,
                [email]
            )
            message = 'Invitation accepted and user created successfully'
        else:
            user.projects.add(project)
            message = 'Invitation accepted and user added to project successfully'

        RefreshToken.for_user(user)

        return Response({'message': message}, status=status.HTTP_200_OK)
