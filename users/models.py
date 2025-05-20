from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.

class ExtendedUser(AbstractUser):
    
    email = models.EmailField(blank=False, unique=True,max_length=255,verbose_name='email')
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=10, blank=True, null=True)
    code_expires_at = models.DateTimeField(blank=True, null=True)
    is_student=models.BooleanField(default=False)
    is_mentor=models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    

    def generate_verification_code(self):
        import random
        code = str(random.randint(100000, 999999))  # 6-digit numeric code
        self.verification_code = code
        self.code_expires_at = timezone.now() + timezone.timedelta(minutes=10)  # code valid for 10 mins
        self.save()
        return code
    
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    
    
# -------------------------------
# Organisation Model
# -------------------------------

# class Organisation(models.Model):
#     user = models.OneToOneField(ExtendedUser, on_delete=models.CASCADE, related_name='organisation_profile')

#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return self.name

# # -------------------------------
# # Advisor Model
# # -------------------------------

# class Advisor(models.Model):
#     user = models.OneToOneField(ExtendedUser, on_delete=models.CASCADE, related_name='advisor_profile')
#     organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='advisors')

#     specialization = models.CharField(max_length=255, blank=True)

#     def __str__(self):
#         return f"Advisor: {self.user.username} ({self.organisation.name})"

# # -------------------------------
# # Student Model
# # -------------------------------

# class Student(models.Model):
#     user = models.OneToOneField(ExtendedUser, on_delete=models.CASCADE, related_name='student_profile')
#     organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='students')

#     enrollment_id = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return f"Student: {self.user.username} ({self.organisation.name})"

# -------------------------------
# Quiz Model
# -------------------------------
class Resource(models.Model):
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name="resources")  # one user → many quizzes
    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.CharField(max_length=3000, blank=False)
    source_file = models.FileField(upload_to="resource_files/", blank=True, null=False)
    ecrypted_src_file = models.FileField(upload_to="resource_files/encrypted/", blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # inserted at
    updated_at = models.DateTimeField(auto_now=True)      # updated at

    def __str__(self):
        return self.name



    



class Questions(models.Model):
    question = models.TextField()
    level = models.CharField(max_length=255)
    mark = models.IntegerField()
    topic = models.CharField(max_length=255)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="resource_questions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

    def __str__(self):
        return self.question[:50] + "..." if len(self.question) > 50 else self.question


    
