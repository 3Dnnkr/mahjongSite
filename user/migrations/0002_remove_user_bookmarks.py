# Generated by Django 4.1 on 2022-08-28 23:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='bookmarks',
        ),
    ]