import graphene

from .utils.generateQuestionsWithResource import generateQuestionFromResource
from .modelType import ExtendedUserType,ResourceType,QuestionsType
from.models import Resource,Questions,ExtendedUser,Subscription
from django.db.models import Q
from graphql_relay import from_global_id

class QuestionQuery(graphene.ObjectType):
    create_question_with_resource = graphene.List(QuestionsType,resId=graphene.ID(required=True))
    fetch_questions_for_resource_id = graphene.List(QuestionsType,resId=graphene.ID(required=True))
    
    def resolve_create_question_with_resource(root,info,resId):
        resource = Resource.objects.get(pk=resId)
        data = generateQuestionFromResource(resource)
        for item in data:
            level = item.get('level', '').strip()
            mark = int(item.get('mark', 0))  # convert to int if needed
            question = item.get('question', '').strip()
            topic = item.get('topic', '').strip()
            quests = Questions.objects.create(
                question=question,
                level=level,
                mark=mark,
                topic=topic,
                resource=resource
            )
            quests.save()
        questions = Questions.objects.filter(resource_id=resource.id).distinct()
        return questions
    def resolve_fetch_questions_for_resource_id(root,info,resId):
        resource = Resource.objects.get(pk=resId)
        questions = Questions.objects.filter(resource_id=resId).distinct()
        return questions
        




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
    


        


