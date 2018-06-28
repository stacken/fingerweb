from django.contrib import admin
from .models import User

class StackenUserAdmin(admin.ModelAdmin):
    list_display = ('username',
                    'first_name',
                    'last_name',
                    'payed_year')

    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('payed_year', 'is_superuser')

    fieldsets = (
        (None, {
            'fields': (
                'first_name',
                'last_name',
                'email'
                )
        }),
        ('Medlemsstatus', {
            'fields': (
                'payed_year',
                ('ths_claimed_vt', 'ths_claimed_ht'),
                ('ths_verified_vt', 'ths_verified_ht'),
                'date_joined'
                )
        }),
        ('Admin', {
            'fields': (
                'is_superuser',
                'is_staff',
                'is_active'
            )
        }),
    )


admin.site.register(User, StackenUserAdmin)
