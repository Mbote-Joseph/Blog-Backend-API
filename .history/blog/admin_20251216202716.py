from django.contrib import admin

from blog.models import Category, Comment, Post, Tag

# Register your models here.
class AdminCategory(admin.ModelAdmin):
    list_display = ('name')
    search_fields = ('name')

class AdminTag(admin.ModelAdmin):
    list_display = ('name')
    search_fields = ('name')
    
class AdminPost(admin.ModelAdmin):
    list_display = ('author', 'category', 'title', 'content', 'is_published', 'created_at', 'tags')
    search_fields = ('author', 'category', 'title', 'content', 'is_published', 'created_at', 'tags')

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)