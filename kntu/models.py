from django.db import models
from django.contrib.auth import get_user_model
import json
import uuid
from ms import ms_api


class Seat(models.IntegerChoices):
        EAST  = 0
        SOUTH = 1
        WEST  = 2
        NORTH = 3

class Release(models.IntegerChoices):
        PUBLIC  = 0, "一般公開"
        LIMIT   = 1, "限定公開(URLを知っている人だけ)"
        PRIVATE = 2, "非公開"

class Examination(models.Model):
    author = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,default=1,verbose_name='投稿者')
    created_datetime = models.DateTimeField('作成日',auto_now_add=True)
    updated_datetime = models.DateTimeField('最終更新日',auto_now=True)
    title = models.CharField('タイトル',max_length=100)
    uuid = models.UUIDField('UUID', primary_key=True, default=uuid.uuid4, editable=False)
    #slug = models.SlugField(blank=False, unique=True)
    description = models.TextField('説明文')
    paifudata = models.JSONField('牌譜データ')
    seat = models.IntegerField('席', choices=Seat.choices, default=0)
    release = models.IntegerField('公開範囲', choices=Release.choices, default=0)

    @property
    def score_infos(self):
        return ms_api.get_scoreinfos_from(self.paifudata, anonymous=True, seat=self.seat, player_name=self.author.username)

    @property
    def paifu_infos(self):
        return ms_api.get_paifuinfos_from(self.paifudata, anonymous=True, seat=self.seat, player_name=self.author.username)

    @property
    def paifu_json(self):
        return json.dumps(self.paifudata)
    

class Kyoku(models.Model):
    exam = models.ForeignKey(Examination, on_delete=models.CASCADE, verbose_name='対象検討', related_name='kyokus')
    name  = models.CharField('局名', max_length=100)
    paifu = models.CharField('牌譜', max_length=9000)


class Comment(models.Model):
    kyoku = models.ForeignKey(Kyoku, on_delete=models.CASCADE, verbose_name='対象局', related_name='comments')
    comment_id = models.IntegerField('コメントID',default=1)
    commenter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True, related_name='exam_comments', verbose_name='発言者')
    posted_at = models.DateTimeField('発言日',auto_now_add=True)
    updated_at = models.DateTimeField('更新日時',auto_now=True)
    is_updated = models.BooleanField('更新されたか',default=False)
    text = models.TextField('本文')
    likers = models.ManyToManyField(get_user_model(),through='CommentLike',blank=True,related_name='like_exam_comments',verbose_name='いいねした人')


class CommentLike(models.Model):
    """ use for order of likers. """
    liker = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='exam_comment_likers')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)

