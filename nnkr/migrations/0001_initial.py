# Generated by Django 4.1 on 2022-08-24 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookmark_datetime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=200, verbose_name='選択肢')),
                ('votes', models.IntegerField(default=0, verbose_name='得票数')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_id', models.IntegerField(default=1, verbose_name='コメントID')),
                ('posted_at', models.DateTimeField(auto_now_add=True, verbose_name='発言日')),
                ('text', models.TextField(verbose_name='本文')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images', verbose_name='画像')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='作成日')),
                ('updated_datetime', models.DateTimeField(auto_now=True, verbose_name='最終更新日')),
                ('title', models.CharField(max_length=100, verbose_name='タイトル')),
                ('description', models.TextField(blank=True, verbose_name='説明文')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='タグ名')),
            ],
        ),
        migrations.CreateModel(
            name='Tagging',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagging_datetime', models.DateTimeField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.question')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.tag')),
            ],
        ),
    ]
