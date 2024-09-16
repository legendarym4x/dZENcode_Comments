from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'), ('published', 'Published'))
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="Title")
    author = models.ForeignKey(User, related_name='blog_posts', on_delete=models.CASCADE)
    body = models.TextField(verbose_name="Body")
    publish = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')

    def get_absolute_url(self):
        return reverse('user_comments:post_detail', args=[self.publish.year, self.publish.strftime('%m'),
                                                          self.publish.strftime('%d'), self.id])

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user_name = models.CharField(max_length=255, verbose_name="User Name", default='user')
    email = models.EmailField(unique=False, verbose_name="E-mail")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    home_page = models.URLField(blank=True, null=True, verbose_name="Home page")
    captcha = models.CharField(max_length=48, verbose_name="CAPTCHA", default='')
    text = models.TextField(verbose_name="Comment Text")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='replies', verbose_name="Parent Comment")

    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name="Image")
    text_file = models.FileField(upload_to='text_files/', blank=True, null=True, verbose_name="Text File")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user_name} on {self.created_at}"


class UserInfo(models.Model):
    user_name = models.CharField(max_length=255, verbose_name="User Name", default='user')
    email = models.EmailField(unique=False, verbose_name="E-mail")
