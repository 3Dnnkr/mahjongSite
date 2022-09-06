from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static


class Icon(models.Model):
    name = models.CharField('アイコン名',max_length=100,default="icon_guest.png")
    order = models.IntegerField('順番',default=0) 

    @property
    def url(self):
        return static("img/icon/" + self.name)

    @classmethod
    def get_default(cls):
        icon, _ = Icon.objects.get_or_create(name='icon_guest.png')
        return icon

    @classmethod
    def get_default_pk(cls):
        icon = cls.get_default()
        return icon.pk


"""
iconのdefaultにIconを使っているためマイグレーション時にエラー発生
django.db.utils.ProgrammingError: relation does not exist
一度iconのderaultを外しmigrateしてからだと上手くいく。
"""
class User(AbstractUser):
    introduction = models.TextField('紹介文',blank=True)
    icon = models.ForeignKey(Icon,blank=True,null=True,verbose_name="アイコン",
        on_delete=models.SET(Icon.get_default),
        default=Icon.get_default_pk)
    #icon = models.ForeignKey(Icon,on_delete=models.PROTECT,blank=True,null=True,verbose_name="アイコン")
    

