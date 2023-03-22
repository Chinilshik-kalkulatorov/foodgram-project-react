from django.contrib import admin

from .models import Subscription, User


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
