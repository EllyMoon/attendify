from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserRegistrationSerializer, UserLoginSerializer, EmailVerificationSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from django.core.mail import send_mail
#from django.conf import settings
#from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import User, EmailVerificationToken, PasswordResetToken
from .utils import EmailService


User = get_user_model()

class UserRegistrationView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(username=email, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EmailVerificationView(APIView):
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = EmailVerificationToken.objects.create(user=user)
                
                # Send verification email using SendGrid
                email_service = EmailService()
                email_service.send_verification_email(email, str(token.token))
                
                return Response({
                    'message': 'Verification email sent successfully'
                })
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = PasswordResetToken.objects.create(user=user)
                
                # Send password reset email using SendGrid
                email_service = EmailService()
                email_service.send_password_reset_email(email, str(token.token))
                
                return Response({
                    'message': 'Password reset email sent successfully'
                })
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                # Check token validity
                reset_token = PasswordResetToken.objects.select_related('user').get(
                    token=token,
                    is_used=False,
                    created_at__gte=timezone.now() - timedelta(hours=24)
                )
                
                user = reset_token.user
                
                # Update password
                user.set_password(new_password)
                user.save()
                
                # Mark token as used
                reset_token.is_used = True
                reset_token.save()
                
                # Send confirmation email
                email_service = EmailService()
                try:
                    email_service.send_password_change_confirmation(user.email)
                except Exception as e:
                    # Log the error but don't prevent password reset
                    print(f"Error sending confirmation email: {str(e)}")
                
                # Invalidate all other reset tokens for this user
                PasswordResetToken.objects.filter(
                    user=user,
                    is_used=False
                ).update(is_used=True)
                
                return Response({
                    'message': 'Password reset successful. You can now login with your new password.'
                }, status=status.HTTP_200_OK)
                
            except PasswordResetToken.DoesNotExist:
                return Response({
                    'error': 'Invalid or expired reset token. Please request a new password reset.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                return Response({
                    'error': 'An error occurred while resetting your password. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)