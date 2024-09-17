from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from captcha import urls as captcha_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('user_comments.urls', namespace='user_comments')),
    path('captcha/', include(captcha_urls)),
]

if settings.DEBUG:
    urlpatterns += (static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) +
                    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
