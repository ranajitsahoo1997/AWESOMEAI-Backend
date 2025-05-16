import graphene
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from .mutations import SendPasswordResetEmail, ResetPassword, Register,ActivateAccount,CreateQuiz,QuizType,UpdateQuiz,DeleteQuiz
# from .queries import QuizType
from.models import Quiz,Question
from django.db.models import Q
from .utils.generate_question_with_resource import generateQuestionFromResource
from graphene_django.types import DjangoObjectType

class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        fields = "__all__"

class QuestionQuery(graphene.ObjectType):
    create_question_with_resource = graphene.List(QuestionType,resId=graphene.ID(required=True))
    
    def resolve_create_question_with_resource(root,info,resId):
        quiz = Quiz.objects.get(pk=resId)
        data = generateQuestionFromResource(quiz)
        for item in data:
            level = item.get('level', '').strip()
            mark = int(item.get('mark', 0))  # convert to int if needed
            text = item.get('questions', '').strip()
            topic = item.get('topic', '').strip()
            question = Question.objects.create(
                text=text,
                level=level,
                mark=mark,
                topic=topic,
                quiz=quiz
            )
            question.save()
        questions = Question.objects.filter(quiz_id=quiz.id).distinct()
        return questions
        




class QuizQuery(graphene.ObjectType):
    all_quizzes = graphene.List(QuizType)
    get_quiz_by_id = graphene.Field(QuizType,
        id=graphene.ID(required=True))
    search_quiz_by_name = graphene.List(QuizType,searchText=graphene.String(required=True))
    
    
    def resolve_all_quizzes(root, info):
        return Quiz.objects.order_by("-updated_at")
    def resolve_get_quiz_by_id(root,info,id):
        return Quiz.objects.get(pk=id)
    def resolve_search_quiz_by_name(root,info,searchText):
        quizzes = Quiz.objects.filter(
             Q(name__icontains=searchText) |
             Q(description__icontains=searchText)
        ).order_by('-created_at')
        return list(quizzes)
    
        

    


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
    

class Query(QuestionQuery,QuizQuery,UserQuery, MeQuery, graphene.ObjectType):
    pass
class Mutation(AuthMutaions, graphene.ObjectType):
    createQuiz = CreateQuiz.Field()
    updateQuiz = UpdateQuiz.Field()
    deleteQuiz = DeleteQuiz.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)