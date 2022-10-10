from django.contrib import admin

from .models import Examination, Kyoku, Comment


class KyokuInline(admin.TabularInline):
    model = Kyoku
    extra = 0

class ExaminationAdmin(admin.ModelAdmin):
    list_display = ('title', 'release', 'author', 'created_datetime', 'updated_datetime',)
    list_display_links = ('title',)
    inlines=(KyokuInline,)


admin.site.register(Examination, ExaminationAdmin)