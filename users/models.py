from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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
    
    

class Resource(models.Model):
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name="resources")  # one user → many quizzes
    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.CharField(max_length=3000, blank=False)
    level = models.CharField(max_length=255)
    mark = models.IntegerField(default=0)
    topic = models.CharField(max_length=255)
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
    public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

    def __str__(self):
        return self.question[:50] + "..." if len(self.question) > 50 else self.question
    
class MyQuestions(models.Model):
    question_text = models.TextField(blank=False,null=False)
    question = models.ForeignKey(Questions,on_delete=models.CASCADE,related_name="my_questions")
    student = models.ForeignKey(ExtendedUser,on_delete=models.CASCADE,related_name="student",limit_choices_to={"is_student": True})
    status = models.CharField(max_length=100,default="Enrolled")
    marks = models.IntegerField(default=10)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True,default=None)
    is_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    


class Subscription(models.Model):
    student = models.ForeignKey(ExtendedUser,on_delete=models.CASCADE,related_name="subscriptions",limit_choices_to={"is_student": True})
    mentor = models.ForeignKey(ExtendedUser,on_delete=models.CASCADE,related_name="subscribers",limit_choices_to={"is_mentor": True})
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.student == self.mentor:
            raise ValidationError("A user cannot subscribe to themselves.")
        if not self.student.is_student:
            raise ValidationError("Only student users can subscribe.")
        if not self.mentor.is_mentor:
            raise ValidationError("You can only subscribe to mentor users.")
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class MyQuestionSubmission(models.Model):
    my_question = models.ForeignKey(MyQuestions, on_delete=models.CASCADE,related_name="submission")
    submitted_answer = models.TextField(blank=False,null=False)
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class SubmissionResult(models.Model):
    my_question_submission = models.ForeignKey(MyQuestionSubmission, on_delete=models.CASCADE, related_name="result")
    question = models.CharField(max_length=1000,blank=False,null=False)
    marks = models.IntegerField(default=0)
    answer = models.TextField(blank=False,null=False)
    expected_length = models.IntegerField(default=0)
    actual_length = models.IntegerField(default=0)
    similarity_score = models.FloatField(default=0.0)
    llm_evaluation_score = models.IntegerField(default=0)
    final_score = models.IntegerField(default=0)
    justification = models.TextField(blank=True, null=True)
    missing_elements = models.TextField(blank=True, null=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"SubmissionResult for {self.my_question_submission.my_question.question_text[:50]} - Score: {self.final_score}"
    
    