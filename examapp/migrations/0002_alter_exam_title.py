# Generated by Django 5.0.6 on 2024-07-27 13:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('examapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='examapp.skills'),
        ),
    ]
