# Generated by Django 4.1 on 2022-09-01 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nnkr', '0009_remove_question_tweet_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='tweet_id',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='TweetID'),
        ),
    ]