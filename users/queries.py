import graphene

from .utils.generateQuestionsWithResource import generateQuestionFromResource
from .modelType import ExtendedUserType,ResourceType,QuestionsType,SubmissionResultType,MyQuestionsType,MyQuestionSubmissionType
from.models import Resource,Questions,ExtendedUser,Subscription,MyQuestionSubmission,MyQuestions,SubmissionResult
from django.db.models import Q
from graphql_relay import from_global_id
import re

class QuestionQuery(graphene.ObjectType):
    create_question_with_resource = graphene.List(QuestionsType,resId=graphene.ID(required=True),froms=graphene.Int(required=True),to=graphene.Int(required=True))
    fetch_questions_for_resource_id = graphene.List(QuestionsType,resId=graphene.ID(required=True))
    fetch_students_for_resource_id = graphene.List(ExtendedUserType,resId=graphene.ID(required=True))
    
    
    def resolve_fetch_students_for_resource_id(root,info,resId):
        resource = Resource.objects.get(pk=resId)
        questionids = Questions.objects.filter(resource_id = resource.id).values_list('id', flat=True).distinct()
        student_ids = MyQuestions.objects.filter(question_id__in=questionids).values_list('student_id', flat=True).distinct()
        print("student_ids",student_ids)
        students = ExtendedUser.objects.filter(id__in=student_ids, is_student=True)
        return students
    
    def resolve_create_question_with_resource(root,info,resId,froms,to):
        resource = Resource.objects.get(pk=resId)
        data = generateQuestionFromResource(resource,froms,to)
        for item in data:
            
            question = item.get('question', '').strip()
            question = re.sub(r'^\d+\.\s*', '', question)
            
            quests = Questions.objects.create(
                question=question,
                level=resource.level,
                mark=resource.mark,
                topic=resource.topic,
                resource=resource
            )
            quests.save()
        questions = Questions.objects.filter(resource_id=resource.id).distinct()
        return questions
    def resolve_fetch_questions_for_resource_id(root,info,resId):
        resource = Resource.objects.get(pk=resId)
        questions = Questions.objects.filter(resource_id=resId).distinct()
        return questions



    
    

class MyQuestionsQuery(graphene.ObjectType):
    fetch_my_questions_for_resource = graphene.List(MyQuestionsType,resId=graphene.ID(required=True),student_id=graphene.ID(required=True))
    
    def resolve_fetch_my_questions_for_resource(root,info,resId,student_id):
        print(student_id)
        # _,student_db_id = from_global_id(student_id)
        questions = Questions.objects.filter(resource_id=resId)
        my_questions = MyQuestions.objects.filter(question__in=questions, student_id=student_id).distinct()
        return my_questions
class MyQuestionsSubmissionQuery(graphene.ObjectType):
    get_my_question_submission_by_my_question =  graphene.Field(MyQuestionSubmissionType,my_question_id = graphene.ID(required=True))
    def resolve_get_my_question_submission_by_my_question(root,info,my_question_id):
        my_question = MyQuestions.objects.get(pk=my_question_id)
        my_question_submission = MyQuestionSubmission.objects.get(my_question=my_question)
        return my_question_submission
    
class SubmissionResultQuery(graphene.ObjectType):
    get_result_for_submission = graphene.Field(SubmissionResultType,submission_id=graphene.ID(required=True))
    
    def resolve_get_result_for_submission(root,info,submission_id):
        submission = MyQuestionSubmission.objects.get(pk=submission_id)
        result = SubmissionResult.objects.get(my_question_submission=submission)
        return result
    get_submission_result_from_my_question = graphene.Field(SubmissionResultType,my_question_id = graphene.ID(required=True))
    
    def resolve_get_submission_result_from_my_question(root,info,my_question_id):
        my_question = MyQuestions.objects.get(pk=my_question_id)
        my_question_submission = MyQuestionSubmission.objects.filter(my_question=my_question).first()
        submission_result = SubmissionResult.objects.filter(my_question_submission=my_question_submission).first()
        if submission_result:
            return submission_result
        return None
    


class ResourceQuery(graphene.ObjectType):
    all_resources = graphene.List(ResourceType)
    get_resource_by_id = graphene.Field(ResourceType,
        id=graphene.ID(required=True))
    
    search_resource_by_name = graphene.List(ResourceType,searchText=graphene.String(required=True))
    
    
    
    def resolve_all_resources(root, info):
        return Resource.objects.order_by("-updated_at")
    def resolve_get_resource_by_id(root,info,id):
        return Resource.objects.get(pk=id)
    def resolve_search_resource_by_name(root,info,searchText):
        resources = Resource.objects.filter(
             Q(name__icontains=searchText) |
             Q(description__icontains=searchText)
        ).order_by('-created_at')
        return list(resources)\
            
class ExtendedUserQuery(graphene.ObjectType):
    all_mentors = graphene.List(ExtendedUserType)
    all_students = graphene.List(ExtendedUserType)
    
    
    def resolve_all_mentors(root,info):
        mentors = ExtendedUser.objects.filter(is_mentor = True)
        return mentors
    def resolve_all_students(root,info):
        students = ExtendedUser.objects.filter(is_student = True)
        return students
    
class SubscriptionQuery(graphene.ObjectType):
    all_subscribed_mentor_ids = graphene.List(graphene.Int,student_id=graphene.String(required=True))
    subscribed_mentors_resources = graphene.List(ResourceType,idsList=graphene.List(graphene.Int,required=True))
    
    def resolve_all_subscribed_mentor_ids(root,info,student_id):
        _,student_db_id = from_global_id(student_id)
        print(student_db_id)
        mentor_ids = Subscription.objects.filter(student_id=student_db_id).values_list("mentor_id",flat=True)
        
        return list(mentor_ids)
    def resolve_subscribed_mentors_resources(root,info,idsList):
        resources = Resource.objects.filter(user_id__in=idsList)
        return resources
    


        


