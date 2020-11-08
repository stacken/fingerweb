from django.contrib import admin
from .models import Service


class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "shortdesc", "nr_users")


admin.site.register(Service, ServiceAdmin)
