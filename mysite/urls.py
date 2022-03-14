from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static 
from django.conf import settings 

urlpatterns = [
    path('admin/', admin.site.urls), #admin(管理画面)の登録
    path('', include('app.urls')), #appの登録
    path('accounts/', include('accounts.urls')), #accountの登録
    path('accounts/', include('allauth.urls')), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 