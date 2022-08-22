from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Question, Choice, Comment, Tag, Tagging


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    min_num = 2
    max_num = 10

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class TaggingInline(admin.TabularInline):
    model = Tagging
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author','created_datetime', 'updated_datetime')
    list_display_links = ('id', 'title')
    filter_horizontal = ('tags',)
    inlines=(TaggingInline, ChoiceInline,CommentInline,)

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')

class TaggingAdmin(admin.ModelAdmin):
    list_display = ('id','question','tag')
    list_display_links = ('id',)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Tagging, TaggingAdmin)