# Generated by Django 5.0.1 on 2024-01-03 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='qno',
            field=models.CharField(max_length=100),
        ),
    ]
