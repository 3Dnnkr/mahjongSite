# Generated by Django 4.1 on 2022-09-02 17:16

from django.db import migrations, models
import django.db.models.deletion
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='icon',
            field=models.ForeignKey(blank=True, default=user.models.get_or_create_guest_icon, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='user.icon', verbose_name='アイコン'),
        ),
    ]
