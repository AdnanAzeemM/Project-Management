from rest_framework.routers import DefaultRouter
from project.views import ProjectViewSet, TaskViewSet
from django.urls import path, include


router = DefaultRouter()

router.register(r'project', ProjectViewSet, basename="project")
router.register(r'task', TaskViewSet, basename="task")
urlpatterns = [
    path('', include(router.urls)),

]