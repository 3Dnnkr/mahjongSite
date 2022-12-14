from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Question, Choice, Comment, CommentLike, Tag, Tagging, Bookmark, Voting, Liker, Disliker, Lobbychat, FAQ


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class TaggingInline(admin.TabularInline):
    model = Tagging
    extra = 0

class BookmarkInline(admin.TabularInline):
    model = Bookmark
    extra = 0

class LikerInline(admin.TabularInline):
    model = Liker
    extra = 0

class DislikerInline(admin.TabularInline):
    model = Disliker
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author','created_datetime', 'updated_datetime', 'tweet_id', 'no_vote')
    list_display_links = ('id', 'title')
    filter_horizontal = ('tags',)
    inlines=(TaggingInline, ChoiceInline, CommentInline, BookmarkInline, LikerInline, DislikerInline)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


class VotingInline(admin.TabularInline):
    model = Voting
    extra = 0

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'votes', 'secret_votes',)
    list_display_links = ('id', 'text')
    filter_horizontal = ('voters',)
    inlines=(VotingInline,)


class CommentLikeInline(admin.TabularInline):
    model = CommentLike
    extra = 0

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'comment_id', 'commenter', 'posted_at',)
    list_display_links = ('id', 'question',)
    filter_horizontal = ('likers',)
    inlines = (CommentLikeInline,)


class TaggingAdmin(admin.ModelAdmin):
    list_display = ('id','question','tag',)
    list_display_links = ('id',)

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id','question','user',)
    list_display_links = ('id',)

class VotingAdmin(admin.ModelAdmin):
    list_display = ('id','choice','voter',)
    list_display_links = ('id',)

class LobbychatAdmin(admin.ModelAdmin):
    list_display = ('id','user','text','posted_at')
    list_display_links = ('id','text',)

class FAQAdmin(admin.ModelAdmin):
    list_display = ('id','question','order')
    list_display_links = ('id','question',)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Lobbychat, LobbychatAdmin)
admin.site.register(FAQ, FAQAdmin)