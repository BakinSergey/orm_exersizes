from django.contrib import admin
from django.db.models import Model
from .models import Post, Tag


# Register your models here.
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ['name', 'tags']
    list_display = ['name', 'show_tags']

    def show_tags(self, obj):
        return "\n".join([a.name for a in obj.tags.all()])



