# hr/views.py

from datetime import timedelta
import logging
from rest_framework.decorators import action, api_view
from rest_framework import status, viewsets, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.conf import settings
import random
import string
import requests
from rest_framework import generics, status

from .models import CustomUser, Department, Leave, Project, Team, Attendance
from .serializers import (
    UserSerializer,  DepartmentSerializer, LeaveSerializer,
    ProjectSerializer, TeamSerializer, AttendanceSerializer, ObtainEmailOTPSerializer, OTPLoginSerializer, HRLoginSerializer, EmailValidationSerializer, HRRegistrationSerializer
)
from .permissions import IsHR, IsSelfOrHR, IsEmployeeSelf

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrHR]

    def perform_create(self, serializer):
        user = serializer.save()
        # Send registration email using ZeptoMail
        try:
            zepto_mail_url = 'https://api.zeptomail.in/v1.1/email'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Zoho-enczapikey {settings.ZEPTOMAIL_TOKEN}',
            }
            data = {
                'from': {
                    'address': settings.ZEPTOMAIL_EMAIL,
                    'name': 'OptiStaff'
                },
                'to': [
                    {
                        'email_address': {
                            'address': user.email
                        }
                    }
                ],
                'subject': 'Registration Successful',
                'htmlbody': f'<p>Dear {user.email},</p><p>Your registration was successful. Welcome! as a {user.role},</p>',
            }

            response = requests.post(zepto_mail_url, headers=headers, json=data)
            
            logging.debug(f"ZeptoMail Response Status: {response.status_code}")
            logging.debug(f"ZeptoMail Response Headers: {response.headers}")
            logging.debug(f"ZeptoMail Response Data: {response.text}")

            if response.status_code != 200 or 'EM_104' in response.text:
                logging.error(f"Registration email: Status code: {response.status_code}, Response: {response.text}")
        
        except Exception as e:
            logging.error(f"An error occurred while sending registration email: {str(e)}")
            
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        max_leaves = user.get_max_leaves()

        current_date = timezone.now()
        first_day_of_month = current_date.replace(day=1)
        last_day_of_month = current_date.replace(day=28) + timedelta(days=4)
        last_day_of_month = last_day_of_month - timedelta(days=last_day_of_month.day)
        leaves_this_month = Leave.objects.filter(
            employee__user=user,
            start_date__range=(first_day_of_month, last_day_of_month)
        ).count()

        if leaves_this_month >= max_leaves:
            return Response({"detail": "You have exceeded the number of leaves you can take this month."},
                            status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class ObtainEmailOTPView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ObtainEmailOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = CustomUser.objects.get(email=email)
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp_code = otp
            user.otp_created_at = timezone.now()
            user.save()

            zepto_mail_url = 'https://api.zeptomail.in/v1.1/email'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Zoho-enczapikey {settings.ZEPTOMAIL_TOKEN}',
            }
            data = {
                'from': {
                    'address': settings.ZEPTOMAIL_EMAIL,
                    'name': 'Your App Name'
                },
                'to': [
                    {
                        'email_address': {
                            'address': email
                        }
                    }
                ],
                'subject': 'Your OTP Code',
                'htmlbody': f'<p>Your OTP code is {otp}</p>',
            }

            response = requests.post(zepto_mail_url, headers=headers, json=data)
            
            logging.debug(f"ZeptoMail Response Status: {response.status_code}")
            logging.debug(f"ZeptoMail Response Headers: {response.headers}")
            logging.debug(f"ZeptoMail Response Data: {response.text}")

            if response.status_code != 200 or 'EM_104' in response.text:
                logging.error(f"Failed to send OTP: Status code: {response.status_code}, Response: {response.text}")
                return Response({'detail': "OTP has been send"}, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return Response({'detail': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'OTP sent successfully'})

class OTPLoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'email': user.email,
                'role': user.role,
                'user_id': user.id
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def hr_dashboard(request):
    total_employees = CustomUser.objects.count()
    absent_today = Attendance.objects.filter(date=timezone.now().date(), check_in__isnull=True).count()
    leaves_today = Leave.objects.filter(start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date()).count()
    
    return Response({
        'total_employees': total_employees,
        'absent_today': absent_today,
        'leaves_today': leaves_today
    })

class HRLoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = HRLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HRRegistrationView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = HRRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

