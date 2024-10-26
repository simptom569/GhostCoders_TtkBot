from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import UserViewSet, EmployeeViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'employees', EmployeeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token),
]