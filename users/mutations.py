# accounts/schema.py

import graphene
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .accounts.tokens import account_password_reset_token
from graphql import GraphQLError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .utils.email import send_verification_code_email
from django.utils import timezone
from validate_email import validate_email
from users.models import Resource
from graphene_file_upload.scalars import Upload
from.models import ExtendedUser,Subscription
import base64
from .utils.sign_creation_for_pdf import sign_create_for_pdf
from .utils.create_digital_signed_pdf import sign_create_for_pdf
from.utils.ChangeExtensionTextToPDF import txt_to_pdf
from django.core.files import File
import os
from .modelType import ResourceType
from graphql_relay import from_global_id

# for encrypt a pdf
from django.core.files.base import ContentFile

# end

User = get_user_model()

def mask_email(email):
    name, domain = email.split('@')
    if len(name) < 6 or len(domain) < 6:
        return email  # fallback
    return name[:4] + '*' * 7 + domain

class SendPasswordResetEmail(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise GraphQLError('User with this email does not exist.')

        token = account_password_reset_token.make_token(user)
        uid = user.pk

        reset_link = f"http://localhost:3000/reset-password/?uid={uid}&token={token}"  # React Frontend URL

         # --- Here is your email sending code ---
        subject = "Reset your password"
        text_content = f"Please click the link to reset your password: {reset_link}"
        html_content = render_to_string('emails/reset_password.html', {
            
            'reset_link': reset_link,
            'user': user,
        })

        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        # --- End of email sending code ---

        return SendPasswordResetEmail(success=True)
    
    
class ResetPassword(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        uid = graphene.ID(required=True)
        token = graphene.String(required=True)
        new_password = graphene.String(required=True)

    def mutate(self, info, uid, token, new_password):
        
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            raise GraphQLError('Invalid user.')

        if not account_password_reset_token.check_token(user, token):
            raise GraphQLError('Invalid or expired token.')

        user.set_password(new_password)
        user.save()

        return ResetPassword(success=True)
    

class Register(graphene.Mutation):
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required = True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)
        role = graphene.String(required=True)
        date_of_birth= graphene.Date(required=True)
        phone_number= graphene.String(required=True)
        
    def mutate(self,info,email,username,password1,password2,role,date_of_birth,phone_number):
        errors=[]
        
        if password1!=password2:
            errors.append("Password do not match")
        if User.objects.filter(email=email).exists():
            errors.append("Email already registered")
        if User.objects.filter(username=username).exists():
            errors.append("Username already taken")
        if errors:
            return Register(success=False,errors = errors)
        
        user = User.objects.create_user(
            email=email,
            username= username,
            password=password1,
            is_active=False,
            is_student= (role=="student"),
            is_mentor= (role=="mentor"),
            date_of_birth=date_of_birth,
            phone_number=phone_number,
        )
        
        #Generating activation token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        email = mask_email(email)
        activation_link = f"http://localhost:3000/activate-user/?uid={uid}&token={token}&email={email}"
        code = user.generate_verification_code()
         # Send activation email
        # send_mail(
        #     subject="Activate Your Account",
        #     message=f"Click the link to activate your account:\n{activation_link}",
        #     from_email="noreply@yourdomain.com",
        #     recipient_list=[email],
        #     fail_silently=False,
        # )
         # --- Here is your email sending code ---
        subject = "Activate Your Account"
        text_content = f"Please click the link to activate your acccount: {activation_link}"
        html_content = render_to_string('emails/verify_account.html', {
            'user': user,
            'verification_link': activation_link,
            'current_year': 2025,
            'code': code,
        })

        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        # --- End of email sending code ---
        
        return Register(success=True, errors=[])
    
class ActivateAccount(graphene.Mutation):
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    class Arguments:
        uid = graphene.String(required=True)
        token = graphene.String(required=True)
        code = graphene.String(required=True)

    def mutate(self, info, uid, token,code):
        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid_decoded)
            if user.is_verified:
                return ActivateAccount(success=False, message="Already verified.")
            if user.verification_code != code:
                return ActivateAccount(success=False, message="Invalid code.")
            if user.code_expires_at and user.code_expires_at < timezone.now():
                return ActivateAccount(success=False, message="Code expired.")
        except Exception:
            return ActivateAccount(success=False, errors=["Invalid UID."])

        if not default_token_generator.check_token(user, token):
            return ActivateAccount(success=False, errors=["Invalid or expired token."])
        print(user)
        user.is_active = True
        user.verification_code = None
        user.code_expires_at = None
        # user.is_verified = True
        print(user)
        user.save()
        return ActivateAccount(success=True, errors=[])
        
  

        
class CreateResource(graphene.Mutation):
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    resource = graphene.Field(ResourceType)
    
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        source_file = Upload(required=True)
        started_at = graphene.DateTime(required=False)
        ended_at = graphene.DateTime(required=False)
        id=graphene.ID()
        
    def mutate(self, info, name, description, source_file=None, started_at=None, ended_at=None,id=None):
        
        id=base64.b64decode(id).decode('utf-8')
        userid = id.split(":")
        print(userid[1])
        print(source_file)
        user = ExtendedUser.objects.get(id=userid[1])
        
        resource = Resource.objects.create(
            user=user,
            name=name,
            description=description,
            source_file=source_file,
            started_at=started_at,
            ended_at=ended_at
        )
        
        input_path = ""
        if resource.source_file.path.endswith(".txt"):
            filePath = resource.source_file.path
            pdfFilePath = filePath.rsplit(".",1)[0]+".pdf"
            updated_input_path=txt_to_pdf(input_txt_path=filePath,output_pdf_path=pdfFilePath)
            with open(updated_input_path, "rb") as f:
                resource.source_file.save(
                    name=os.path.basename(updated_input_path),
                    content=File(f),
                    save=True  # Save the model after updating
                )
            input_path = resource.source_file.path
        else:
            input_path = resource.source_file.path
        print(input_path)
        ## create signed pdf here
        output_buffer = sign_create_for_pdf(input_pdf_path=input_path,output_pdf_path="signed_file5.pdf")
        
        
        
        # Save encrypted PDF to model
        encrypted_src_filename = f"encrypted_{resource.source_file.name.split('/')[-1]}"
        resource.ecrypted_src_file.save(encrypted_src_filename,ContentFile(output_buffer.getvalue()))
        resource.save()
        
        
        
        return CreateResource(success=True,errors=[],resource=resource)


class UpdateResource(graphene.Mutation):
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        source_file = Upload(required=False)

    def mutate(self, info, id, name, description, source_file=None):
        try:
            resource = Resource.objects.get(pk=id)
            resource.name = name
            resource.description = description

            if source_file:
                resource.source_file = source_file  # Only update if a new file is provided

            resource.save()
            return UpdateResource(success=True, errors=[])
        except Resource.DoesNotExist:
            return UpdateResource(success=False, errors=["Resource not found"])
        except Exception as e:
            return UpdateResource(success=False, errors=[str(e)])
        
class DeleteResource(graphene.Mutation):
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    class Arguments:
        id = graphene.ID(required=True)
        
    def mutate(self,info,id):
        try:
            resource = Resource.objects.get(pk=id)
            resource.delete()
            return DeleteResource(success=True,errors=[])
        except Resource.DoesNotExist:
            return DeleteResource(success=False,errors=['Resource not found'])
        except Exception as e:
            return DeleteResource(success=False, errors=[str(e)])
        
class SubscribeMentor(graphene.Mutation):
    class Arguments:
        mentor_id = graphene.Int(required=True)
        student_id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, mentor_id, student_id):
        try:
            _, student_db_id = from_global_id(student_id)
            exists = Subscription.objects.filter(mentor_id=mentor_id,student_id=student_db_id).exists()
            if exists:
                return SubscribeMentor(success=False, errors=["You have already Subscribed"])
            else:
                student = ExtendedUser.objects.get(id=student_db_id)
                mentor = ExtendedUser.objects.get(id=mentor_id)
                Subscription.objects.create(student=student, mentor=mentor)
                return SubscribeMentor(success=True, errors=[])
        except Exception as e:
            return SubscribeMentor(success=False, errors=[str(e)])
        

    
        
        
        
        
