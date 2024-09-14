from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('captcha/', include('captcha.urls')),
]
