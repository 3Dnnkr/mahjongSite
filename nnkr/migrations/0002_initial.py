# Generated by Django 4.1 on 2022-10-10 14:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nnkr', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='voting',
            name='voter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tagging',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.question'),
        ),
        migrations.AddField(
            model_name='tagging',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagging', to='nnkr.tag'),
        ),
        migrations.AddField(
            model_name='question',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='投稿者'),
        ),
        migrations.AddField(
            model_name='question',
            name='bookmarkers',
            field=models.ManyToManyField(blank=True, related_name='bookmarks', through='nnkr.Bookmark', to=settings.AUTH_USER_MODEL, verbose_name='ブックマーカー'),
        ),
        migrations.AddField(
            model_name='question',
            name='dislikers',
            field=models.ManyToManyField(blank=True, related_name='dislikes', through='nnkr.Disliker', to=settings.AUTH_USER_MODEL, verbose_name='否定したユーザー'),
        ),
        migrations.AddField(
            model_name='question',
            name='likers',
            field=models.ManyToManyField(blank=True, related_name='likes', through='nnkr.Liker', to=settings.AUTH_USER_MODEL, verbose_name='評価したユーザー'),
        ),
        migrations.AddField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(related_name='questions', through='nnkr.Tagging', to='nnkr.tag', verbose_name='タグ'),
        ),
        migrations.AddField(
            model_name='lobbychatlike',
            name='liker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lobbychatlike',
            name='lobbychat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.lobbychat'),
        ),
        migrations.AddField(
            model_name='lobbychat',
            name='likers',
            field=models.ManyToManyField(blank=True, related_name='like_lobbycahts', through='nnkr.LobbychatLike', to=settings.AUTH_USER_MODEL, verbose_name='いいねした人'),
        ),
        migrations.AddField(
            model_name='lobbychat',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='loby_chats', to=settings.AUTH_USER_MODEL, verbose_name='発言者'),
        ),
        migrations.AddField(
            model_name='liker',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.question'),
        ),
        migrations.AddField(
            model_name='liker',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='disliker',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.question'),
        ),
        migrations.AddField(
            model_name='disliker',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.comment'),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='liker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='commenter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='発言者'),
        ),
        migrations.AddField(
            model_name='comment',
            name='likers',
            field=models.ManyToManyField(blank=True, related_name='like_comments', through='nnkr.CommentLike', to=settings.AUTH_USER_MODEL, verbose_name='いいねした人'),
        ),
        migrations.AddField(
            model_name='comment',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='nnkr.question', verbose_name='対象質問'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.question'),
        ),
        migrations.AddField(
            model_name='choice',
            name='voters',
            field=models.ManyToManyField(blank=True, through='nnkr.Voting', to=settings.AUTH_USER_MODEL, verbose_name='投票者'),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nnkr.question'),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
