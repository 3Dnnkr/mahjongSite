from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from nnkr.models import Bookmark

class BookmarkInline(admin.TabularInline):
    model = Bookmark
    extra = 0

class AdminUserAdmin(UserAdmin):
    list_display = ('id','username','date_joined','last_login')
    list_display_links = ('id','username')
    inlines = (BookmarkInline,)

admin.site.register(get_user_model(), AdminUserAdmin)
