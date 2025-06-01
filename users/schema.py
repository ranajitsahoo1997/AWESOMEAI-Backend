import graphene
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from .mutations import SendPasswordResetEmail, ResetPassword, Register,ActivateAccount,CreateResource,UpdateResource,DeleteResource,SubscribeMentor,CreateMyQuestions,UpdateMyQuestionsStatus
from.mutations import CreateMyQuestionSubmission,GenerateAnswerSheet
from .queries import QuestionQuery,ResourceQuery,ExtendedUserQuery,SubscriptionQuery,SubmissionResultQuery,MyQuestionsQuery,MyQuestionsSubmissionQuery



       

    


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
    

class Query(MyQuestionsSubmissionQuery,MyQuestionsQuery,SubmissionResultQuery,SubscriptionQuery,ExtendedUserQuery,QuestionQuery,ResourceQuery,UserQuery, MeQuery, graphene.ObjectType):
    pass
class Mutation(AuthMutaions, graphene.ObjectType):
    createResource = CreateResource.Field()
    updateResource = UpdateResource.Field()
    deleteResource = DeleteResource.Field()
    subscribeMentor = SubscribeMentor.Field()
    createMyQuestions = CreateMyQuestions.Field()
    updateMyQuestionsStatus = UpdateMyQuestionsStatus.Field()
    createMyQuestionSubmission = CreateMyQuestionSubmission.Field()
    generateAnswerSheet = GenerateAnswerSheet.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)