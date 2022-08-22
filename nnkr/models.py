from django.db import models
from django.contrib.auth import get_user_model


class Tag(models.Model):
    name = models.CharField('タグ名',max_length=32)

    def __str__(self):
        return self.name

class Question(models.Model):
    author = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,default=1,verbose_name='投稿者')
    image = models.ImageField('画像',upload_to='images')
    created_datetime = models.DateTimeField('作成日',auto_now_add=True)
    updated_datetime = models.DateTimeField('最終更新日',auto_now=True)
    title = models.CharField('タイトル',max_length=100)
    description = models.TextField('説明文',blank=True)
    tags = models.ManyToManyField(Tag, through='Tagging',blank=True, verbose_name='タグ')

    def __str__(self):
        return self.title
    
    def get_sum_of_votes(self):
        sum = 0
        for choice in self.choice_set.all():
            sum += choice.votes
        return sum

    def get_num_of_comments(self):
        return self.comment_set.all().count()

class Tagging(models.Model):
    """ use for order of tags. """
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tagging_datetime = models.DateTimeField()

class Comment(models.Model):
    target = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='対象質問')
    comment_id = models.IntegerField('コメントID',default=1)
    commenter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, verbose_name='発言者')
    posted_at = models.DateTimeField('発言日',auto_now_add=True)
    text = models.TextField('本文')

class Choice(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    choice_text = models.CharField('選択肢',max_length=200)
    votes = models.IntegerField('得票数',default=0)
    def __str__(self):
        return self.choice_text
    def get_voterate(self):
        choices = Choice.objects.filter(question=self.question)
        sum = 0
        for choice in choices:
            sum += choice.votes
        return 0 if sum==0 else 100*self.votes/sum