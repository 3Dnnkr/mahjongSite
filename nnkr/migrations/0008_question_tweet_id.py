# Generated by Django 4.1 on 2022-09-01 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nnkr', '0007_commentlike_rename_target_comment_question_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='tweet_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='TweetID'),
        ),
    ]