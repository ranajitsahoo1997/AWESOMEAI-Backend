from django.contrib import admin
from .models import ExtendedUser, Organisation, Advisor, Student,Quiz
from django.apps import apps
# Register your models here.

admin.site.register(ExtendedUser)
admin.site.register(Organisation)
admin.site.register(Advisor)
admin.site.register(Student)
admin.site.register(Quiz)

app = apps.get_app_config('graphql_auth')

for model_name,model in app.models.items():
    admin.site.register(model)



