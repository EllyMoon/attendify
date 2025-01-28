from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To
from django.conf import settings


class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = Email(settings.DEFAULT_FROM_EMAIL)

    def send_verification_email(self, user_email, verification_token):
        to_email = To(user_email)
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token}"
        
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject='Verify Your Email Address',
            html_content=f'''
                <h2>Email Verification</h2>
                <p>Please click the link below to verify your email address:</p>
                <a href="{verification_url}">Verify Email</a>
                <p>If you didn't request this, please ignore this email.</p>
            '''
        )
        
        try:
            response = self.sg.send(message)
            return response.status_code
        except Exception as e:
            print(f"Error sending verification email: {str(e)}")
            raise

    def send_password_reset_email(self, user_email, reset_token):
        to_email = To(user_email)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
        
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject='Reset Your Password',
            html_content=f'''
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password. Click the link below to proceed:</p>
                <a href="{reset_url}">Reset Password</a>
                <p>If you didn't request this, please ignore this email.</p>
                <p>This link will expire in 24 hours.</p>
            '''
        )
        
        try:
            response = self.sg.send(message)
            return response.status_code
        except Exception as e:
            print(f"Error sending password reset email: {str(e)}")
            raise

def send_password_change_confirmation(self, user_email):
    to_email = To(user_email)
    
    message = Mail(
        from_email=self.from_email,
        to_emails=to_email,
        subject='Password Changed Successfully',
        html_content='''
            <h2>Password Changed</h2>
            <p>Your password has been successfully changed.</p>
            <p>If you did not make this change, please contact support immediately.</p>
        '''
    )
    
    try:
        response = self.sg.send(message)
        return response.status_code
    except Exception as e:
        print(f"Error sending password change confirmation: {str(e)}")
        raise        