# Generated by Django 4.1 on 2022-09-08 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nnkr', '0005_alter_question_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='description',
            field=models.TextField(verbose_name='説明文'),
        ),
    ]