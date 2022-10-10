# Generated by Django 4.1 on 2022-10-10 14:48

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='icon',
            field=models.ForeignKey(blank=True, default=user.models.Icon.get_default_pk, null=True, on_delete=models.SET(user.models.Icon.get_default), to='user.icon', verbose_name='アイコン'),
        ),
    ]
