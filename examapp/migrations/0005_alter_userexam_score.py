# Generated by Django 5.0.6 on 2024-07-05 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('examapp', '0004_profile_userexam'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userexam',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]