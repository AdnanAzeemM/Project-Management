from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from project.models import Project


class User(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_group',
        blank=True,
        help_text='The groups this user belongs toa users.',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='custom_user_permissions'
    )
    password = models.CharField(max_length=255, )

    projects = models.ManyToManyField(Project, related_name='user_project', blank=True, )

    def __str__(self):
        return self.username

