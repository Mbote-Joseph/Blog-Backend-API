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
    
class AdminComment(admin.ModelAdmin):
    list_display = ('post', 'user', 'comment', 'is_approved', 'created_at')
    search_fields = ('post', 'user', 'comment', 'is_approved', 'created_at')

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)