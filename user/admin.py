from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

class AdminUserAdmin(UserAdmin):
    list_display = ('id','username','date_joined','last_login')
    list_display_links = ('id','username')

admin.site.register(get_user_model(), AdminUserAdmin)
