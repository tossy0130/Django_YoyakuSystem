from django.contrib import admin

# Register your models here.
from .models import Store, Staff, Booking

# 店舗一覧　
admin.site.register(Store)
# スタッフ一覧
admin.site.register(Staff)
# 予約部分
admin.site.register(Booking)
