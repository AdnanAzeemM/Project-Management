from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, GroupViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'roles', GroupViewSet)
# router.register(r'permissions', CustomPermissionViewSet)

urlpatterns = [
    path('', include(router.urls))
]