from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from cloudinary.models import CloudinaryField
import cloudinary


class Question(models.Model):
    author = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,default=1,verbose_name='投稿者')
    #image = models.ImageField('画像',upload_to='images',blank=True,null=True)
    image = CloudinaryField('画像',folder='media/images')
    created_datetime = models.DateTimeField('作成日',auto_now_add=True)
    updated_datetime = models.DateTimeField('最終更新日',auto_now=True)
    title = models.CharField('タイトル',max_length=100)
    description = models.TextField('説明文',blank=True)
    tags = models.ManyToManyField('Tag', through='Tagging',blank=True, verbose_name='タグ',related_name='questions')
    tweet_id = models.CharField('TweetID', max_length=200, blank=True, null=True)
    no_vote = models.BooleanField('投票機能を使わない', default=False)

    bookmarkers = models.ManyToManyField(get_user_model(),through='Bookmark',blank=True,related_name='bookmarks',verbose_name='ブックマーカー')
    likers = models.ManyToManyField(get_user_model(),through='Liker',blank=True,related_name='likes',verbose_name='評価したユーザー')
    dislikers = models.ManyToManyField(get_user_model(),through='Disliker',blank=True,related_name='dislikes',verbose_name='否定したユーザー')

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        #self.image.delete() # if image is ImageField
        cloudinary.uploader.destroy(self.image.public_id) # if image is CloudinaryField
        super(Question, self).delete(*args, **kwargs)

    @property
    def votes(self):
        return sum( [c.votes for c in self.choice_set.all()] )

    @property
    def voters(self):
        _voters = get_user_model().objects.none()
        for c in self.choice_set.all():
            _voters = c.voters.union(_voters)
        return _voters
    
    @property
    def rating(self):
        return self.likers.all().count() - self.dislikers.all().count()


class Tag(models.Model):
    name = models.CharField('タグ名', unique=False, blank=False, max_length=32)

    def __str__(self):
        return self.name

class Tagging(models.Model):
    """ use for order of tags. """
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tagging_datetime = models.DateTimeField()

class Bookmark(models.Model):
    """ use for order of bookmarks. """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    bookmark_datetime = models.DateTimeField()

class Liker(models.Model):
    """ use for order of likers. """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

class Disliker(models.Model):
    """ use for order of dislikers. """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='対象質問', related_name='comments')
    comment_id = models.IntegerField('コメントID',default=1)
    commenter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True, related_name='comments', verbose_name='発言者')
    posted_at = models.DateTimeField('発言日',auto_now_add=True)
    updated_at = models.DateTimeField('更新日時',auto_now=True)
    is_updated = models.BooleanField('更新されたか',default=False)
    text = models.TextField('本文')
    likers = models.ManyToManyField(get_user_model(),through='CommentLike',blank=True,related_name='like_comments',verbose_name='いいねした人')

class CommentLike(models.Model):
    """ use for order of likers. """
    liker = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)

class Choice(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    text = models.CharField('選択肢',max_length=200)
    secret_votes = models.IntegerField('無記名得票数',default=0) 
    voters = models.ManyToManyField(get_user_model(), through='Voting',blank=True, verbose_name='投票者')
    
    def __str__(self):
        return self.text
    
    @property
    def votes(self):
        return self.secret_votes + self.voters.all().count()
    
    @property
    def voterate(self):
        sum_votes = sum([c.votes for c in Choice.objects.filter(question=self.question)])
        return 0 if sum_votes==0 else 100*self.votes/sum_votes

class Voting(models.Model):
    """ use for order of voters. """
    voter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    choice = models.ForeignKey('Choice', on_delete=models.CASCADE)
    voting_datetime = models.DateTimeField()


class Lobbychat(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True, related_name='loby_chats', verbose_name='発言者')
    posted_at = models.DateTimeField('発言日',auto_now_add=True)
    updated_at = models.DateTimeField('更新日時',auto_now=True)
    is_updated = models.BooleanField('更新されたか',default=False)
    text = models.TextField('本文')