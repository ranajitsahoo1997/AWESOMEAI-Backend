# Generated by Django 3.2.25 on 2025-05-19 19:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20250519_1944'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='user',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='question',
        ),
        migrations.AlterField(
            model_name='option',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='users.questions'),
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Quiz',
        ),
    ]
