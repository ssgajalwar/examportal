# Generated by Django 5.0.6 on 2024-08-18 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('examapp', '0006_userresponse_exam_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userresponse',
            name='selected_choice',
            field=models.IntegerField(),
        ),
    ]