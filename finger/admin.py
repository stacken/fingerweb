from django.contrib import admin
from .models import User
from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse
from datetime import datetime, timedelta

class MemberListFilter(admin.SimpleListFilter):
    title = "Member Status/Type"
    parameter_name = 'member_status'

    def lookups(self, request, model_admin):
        return (
            ('active', "Active Member"),
            ('recent', "Recent Member"),
        )

    def active_member(self, request, queryset):
        """
        List members that we consider active. Members that have
        payed this year, have verified their THS status the last
        half year or are honorary members. New members that
        joined the last year are also considered active.

        Inactive accounts are filtered out, we do not look at the
        date_parted field because we assume is_active should be
        false for these users.
        """
        t = datetime.now()

        if t.month <= 7:
            ths_member_claimed = Q(ths_claimed_vt__gte=t.year)
        else:
            ths_member_claimed = Q(ths_claimed_ht__gte=t.year)

        return queryset.filter(
            Q(payed_year__gte=t.year) |
            Q(honorary_member__exact=True) |
            Q(date_joined__gte=t - timedelta(days=365)) |
            ths_member_claimed
        ).exclude(is_active__exact=False)

    def recent_member(self, request, queryset):
        """
        List members that recently where members. Members that
        has a parted date and are active will be filtered out.
        """
        t = datetime.now() - timedelta(days=2*365)

        return queryset.filter(
            Q(payed_year__gte=t.year) |
            Q(ths_claimed_vt__gte=t.year) |
            Q(ths_claimed_ht__gte=t.year)
        ).exclude(date_parted__lte=datetime.now()) \
         .exclude(honorary_member__exact=True) \
         .difference(self.active_member(request, queryset))

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return self.active_member(request, queryset)
        if self.value() == 'recent':
            return self.recent_member(request, queryset)


class MemberTHSStatus(admin.SimpleListFilter):
    t = datetime.now()
    is_vt = t.month <= 7
    title = f"THS Status VT{t.year}" if is_vt else f"THS Status HT{t.year}"

    parameter_name = 'ths_status'

    def lookups(self, request, model_admin):
        return (
            ('claimed', "Claimed"),
            ('verified', "Verified"),
        )

    def queryset(self, request, queryset):
        t = datetime.now()

        if self.value() == 'claimed':
            if self.is_vt:
                return queryset.filter(Q(ths_claimed_vt__exact=t.year))
            else:
                return queryset.filter(Q(ths_claimed_ht__exact=t.year))
        if self.value() == 'verified':
            if self.is_vt:
                return queryset.filter(Q(ths_verified_vt__exact=t.year))
            else:
                return queryset.filter(Q(ths_verified_ht__exact=t.year))

def export_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/json")
    serializers.serialize("json", queryset, stream=response)
    response['Content-Disposition'] = 'attachment; filename=users.json'
    return response
export_json.short_description = "Export as JSON"

class StackenUserAdmin(admin.ModelAdmin):
    list_display = ('username',
                    'get_full_name',
                    'last_member',
                    'is_member',
                    'ths_claimed',
                    'ths_verified',
                    'support_member')

    search_fields = ('username',
                     'first_name',
                     'last_name',
                     'ths_name',
                     'kth_account')

    list_filter = (MemberListFilter,
                   'support_member',
                   'honorary_member',
                   MemberTHSStatus,
                   'has_key',
                   'is_superuser')

    actions = [export_json]

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
