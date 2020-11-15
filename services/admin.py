from django.contrib import admin
from .models import Service
from .models import ServiceUser


class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "shortdesc", "nr_users")


class ServiceUserAdmin(admin.ModelAdmin):
    list_display = ("service", "user", "modified")


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceUser, ServiceUserAdmin)
