from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import Icon

class IconAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order')
    list_display_links = ('id', 'name')

class AdminUserAdmin(UserAdmin):
    list_display = ('id','username','date_joined','last_login',)
    list_display_links = ('id','username')
    fieldsets = UserAdmin.fieldsets + (
            ('Extra Fields', {'fields': ('introduction','icon',)}),
    )

admin.site.register(Icon, IconAdmin)
admin.site.register(get_user_model(), AdminUserAdmin)
