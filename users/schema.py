import graphene
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from .mutations import SendPasswordResetEmail, ResetPassword, Register,ActivateAccount,CreateResource,UpdateResource,DeleteResource,ResourceType
# from .queries import ResourceType
from.models import Resource,Questions
from django.db.models import Q
# from .utils.generate_question_with_resource import generateQuestionFromResource
from .utils.generateQuestionsWithResource import generateQuestionFromResource
from graphene_django.types import DjangoObjectType

class QuestionsType(DjangoObjectType):
    class Meta:
        model = Questions
        fields = "__all__"

class QuestionQuery(graphene.ObjectType):
    create_question_with_resource = graphene.List(QuestionsType,resId=graphene.ID(required=True))
    
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
        return list(resources)
    
        

    


class AuthMutaions(graphene.ObjectType):
    register = Register.Field()
    verify_account = ActivateAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    update_account = mutations.UpdateAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    send_password_reset_email = SendPasswordResetEmail.Field()
    # password_reset = mutations.PasswordReset.Field()
    password_reset = ResetPassword.Field()
    password_change = mutations.PasswordChange.Field()
    logout = mutations.RevokeToken.Field()
    verify_token = mutations.VerifyToken.Field()
    

class Query(QuestionQuery,ResourceQuery,UserQuery, MeQuery, graphene.ObjectType):
    pass
class Mutation(AuthMutaions, graphene.ObjectType):
    createResource = CreateResource.Field()
    updateResource = UpdateResource.Field()
    deleteResource = DeleteResource.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)