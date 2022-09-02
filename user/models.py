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

def get_or_create_guest_icon():
    icon, _ = Icon.objects.get_or_create(name='icon_guest.png')
    return icon

class User(AbstractUser):
    introduction = models.TextField('紹介文',blank=True)
    icon = models.ForeignKey(Icon,on_delete=models.SET_DEFAULT,blank=True,null=True,verbose_name="アイコン",default=get_or_create_guest_icon)

