# hr/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, DepartmentViewSet, LeaveViewSet, ProjectViewSet, TeamViewSet, AttendanceViewSet, ObtainEmailOTPView, OTPLoginView,hr_dashboard,HRLoginView,HRRegistrationView, UserProfileView
# HRLoginView, HRRegistrationView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'attendance', AttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/obtain-email-otp/', ObtainEmailOTPView.as_view(), name='obtain-email-otp'),
    path('auth/otp-login/', OTPLoginView.as_view(), name='otp-login'),
    path('auth/hr-login/', HRLoginView.as_view(), name='hr-login'),
    path('auth/hr-register/', HRRegistrationView.as_view(), name='hr-register'),
    path('hr-dashboard/', hr_dashboard, name='hr-dashboard'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
