
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphene_file_upload.django import FileUploadGraphQLView
from users.schema import schema
from django.conf.urls.static import static
from .settings import MEDIA_ROOT,MEDIA_URL



print(MEDIA_ROOT)
urlpatterns = [
    path('admin/', admin.site.urls),
    
    
    # path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))), 
    path("graphql/", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True, schema=schema))),
   
   
]+static(MEDIA_URL,document_root=MEDIA_ROOT)
