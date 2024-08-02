from django.db import models
from django.utils.crypto import get_random_string


class Project(models.Model):
    project_name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.project_name


class Invitation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    message = models.TextField()
    token = models.CharField(max_length=64, null=True, blank=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(length=25)
        super().save(*args, **kwargs)


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name
