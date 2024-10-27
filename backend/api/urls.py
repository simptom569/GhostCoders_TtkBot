from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views 

from .views import UserViewSet, EmployeeViewSet, RequestViewSet, IntentViewSet, SubintentViewSet, PhraseViewSet, EmailRecipientViewSet, SendEmailAPIView, AudioIntentViewSet, TextIntentViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'requests', RequestViewSet)
router.register(r'intent', IntentViewSet)
# router.register(r'subintent', SubintentViewSet)
router.register(r'subintent', SubintentViewSet, basename='subintent')
router.register(r'phrase', PhraseViewSet)
router.register(r'email-recipients', EmailRecipientViewSet, basename='email-recipient')



urlpatterns = [
    path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token),
    path('audio-intent/', AudioIntentViewSet.as_view(), name='audio-intent'),
    path('text-intent/', TextIntentViewSet.as_view(), name='text-intent'),
    path('send-email/', SendEmailAPIView.as_view(), name='send-email'),
]