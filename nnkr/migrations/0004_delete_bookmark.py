# Generated by Django 4.1 on 2022-08-28 23:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_remove_user_bookmarks'),
        ('nnkr', '0003_alter_comment_commenter'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Bookmark',
        ),
    ]