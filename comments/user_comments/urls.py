from django.urls import path, include
from . import views

app_name = 'user_comments'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('captcha/', include('captcha.urls')),
    path('get_captcha/', views.get_captcha, name='get_captcha'),
    path('api/v1/comments/<int:year>/<int:month>/<int:day>/<int:post_id>/', views.CommentAPIView.as_view(),
         name='comment-list'),
    path('api/v1/comments/<int:year>/<int:month>/<int:day>/<int:post_id>/create/', views.CommentAPIView.as_view(),
         name='create-comment'),

]
