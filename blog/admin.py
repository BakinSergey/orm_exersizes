from django.contrib import admin
from django.db.models import Model
from .models import Post, Tag


# Register your models here.
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ['name']


class TagInline(admin.StackedInline):
    model = Post.tags.through


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ['name', 'tags']
    list_display = ['name', 'show_tags']

    inlines = (TagInline,)

    def show_tags(self, obj):
        return " .___. ".join([a.name for a in obj.tags.all()])


