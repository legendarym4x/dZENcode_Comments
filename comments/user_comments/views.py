from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import CommentForm
from .models import Post


class PostListView(View):
    def get(self, request):
        posts = Post.objects.all()
        for post in posts:
            post.formatted_date = post.publish.strftime('%Y/%m/%d')
        return render(request, 'comments/index.html', {'posts': posts})


class PostDetailView(View):
    def get(self, request, year, month, day, post_id):
        post = get_object_or_404(Post, id=post_id, status='published', publish__year=year, publish__month=month, publish__day=day)
        return render(request, 'comments/detail.html', {
            'post': post,
            'comment_form': CommentForm(),
            'post_id': post.id,
            'year': post.publish.year,
            'month': post.publish.month,
            'day': post.publish.day
        })
