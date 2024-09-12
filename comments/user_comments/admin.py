from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email', 'text', 'created_at', 'updated_at')
    search_fields = ('user_name', 'email', 'text')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

