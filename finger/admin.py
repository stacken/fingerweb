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
                ths_member_claimed = Q(ths_claimed_vt__gte=t.year)
            else:
                ths_member_claimed = Q(ths_claimed_ht__gte=t.year)

            # If this is "active" t will be in the future, disabling this
            # option. If this is "recent" t is already two years ago so
            # is_new_member will be increased to only "1 year ago".
            is_new_member = Q(date_joined__gte=t + timedelta(days=365))

            return queryset.filter(
                Q(payed_year__gte=t.year) |
                Q(honorary_member__exact=True) |
                is_new_member |
                ths_member_claimed
            ).exclude(is_active__exact=False)

class StackenUserAdmin(admin.ModelAdmin):
    list_display = ('username',
                    'first_name',
                    'last_name',
                    'payed_year')

    search_fields = ('username',
                     'first_name',
                     'last_name',
                     'ths_name',
                     'kth_account')

    list_filter = ('support_member',
                   'honorary_member',
                   MemberStatusListFilter,
                   'has_key',
                   'payed_year',
                   'is_superuser')

    fieldsets = (
        (None, {
            'fields': (
                'username',
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
