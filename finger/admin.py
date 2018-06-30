from django.contrib import admin
from .models import User
from django.db.models import Q
from datetime import datetime, timedelta

class MemberStatusListFilter(admin.SimpleListFilter):
    title = "Members Status"
    parameter_name = 'member_status'

    def lookups(self, request, model_admin):
        return (
            ('active', "Active"),
            ('recent', "Recent"),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active' or self.value() == 'recent':

            if self.value() == 'active':
                t = datetime.now()
            else:
                t = datetime.now() - timedelta(days=2*365)

            if t.month <= 7:
                ths_member_verified = Q(ths_verified_vt__gte=t.year)
            else:
                ths_member_verified = Q(ths_verified_ht__gte=t.year)

            return queryset.filter(
                Q(payed_year__gte=t.year) |
                Q(honorary_member__exact=True) |
                ths_member_verified
            ).exclude(is_active__exact=False)

class StackenUserAdmin(admin.ModelAdmin):
    list_display = ('username',
                    'first_name',
                    'last_name',
                    'payed_year')

    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('support_member',
                   'honorary_member',
                   MemberStatusListFilter,
                   'payed_year',
                   'is_superuser')

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'first_name',
                'last_name',
                'email',
                'address',
                'phone',
                'comments'
                )
        }),
        ('Medlemsstatus', {
            'fields': (
                'payed_year',
                ('ths_verified_vt', 'ths_verified_ht'),
                ('date_joined', 'date_parted'),
                ('honorary_member', 'support_member')
                )
        }),
        ('Access', {
            'fields': (
                'has_key',
                'keycard_number'
                )
        }),
        ('Kåren', {
            'fields': (
                'ths_name',
                ('ths_claimed_vt', 'ths_claimed_ht'),
                'kth_account'
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
