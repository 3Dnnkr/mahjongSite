# Generated by Django 4.1 on 2022-09-09 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nnkr', '0006_alter_question_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=100, verbose_name='タイトル')),
                ('answer', models.TextField(verbose_name='本文')),
                ('order', models.IntegerField(default=0, verbose_name='順番')),
            ],
        ),
    ]
