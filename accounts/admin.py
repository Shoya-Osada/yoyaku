from django.contrib import admin

from .models import CustomUser

#管理画面でもCustomUserを編集できるように設定。
admin.site.register(CustomUser)