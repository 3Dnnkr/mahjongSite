# Generated by Django 4.1 on 2022-09-03 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nnkr', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='no_vote',
            field=models.BooleanField(default=False, verbose_name='投票機能を使わない'),
        ),
    ]
