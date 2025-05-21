from graphene_django.types import DjangoObjectType
from.models import ExtendedUser,Resource,Questions
import graphene

class ExtendedUserType(DjangoObjectType):
    class Meta:
        model = ExtendedUser
        fields = "__all__"
        
class ResourceType(DjangoObjectType):
    class Meta:
        model = Resource
        fields = "__all__"
        
    source_file_url= graphene.String()
    ecrypted_src_file_url = graphene.String()
    def resolve_source_file_url(self, info):
        if self.source_file:
           return info.context.build_absolute_uri(self.source_file.url)
        return None
    def resolve_ecrypted_src_file_url(self,info):
        if self.ecrypted_src_file:
            return info.context.build_absolute_uri(self.ecrypted_src_file.url)
        
class QuestionsType(DjangoObjectType):
    class Meta:
        model = Questions
        fields = "__all__"