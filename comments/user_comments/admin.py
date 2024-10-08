from django.contrib import admin
from .models import Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email', 'text', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'email', 'body')
    ordering = ('-created_at',)


admin.site.register(Comment, CommentAdmin)
