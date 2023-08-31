from django.contrib import admin
from .models import User
from .models import Member
from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from datetime import datetime, timedelta
from django.urls import reverse
from django.utils.html import escape, mark_safe
from post_office import mail
from post_office.models import EmailTemplate
import csv


class MemberListFilter(admin.SimpleListFilter):
    title = "Member Status/Type"
    parameter_name = "member_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active Member"),
            ("recent", "Recent Member"),
        )

    def ths_member_claimed(self):
        t = datetime.now()
        if t.month <= 8:
            return Q(ths_claimed_vt__gte=t.year)
        return Q(ths_claimed_ht__gte=t.year)

    def active_member(self, request, queryset):
        """
        List members that we consider active. Members that have
        paid this year, have verified their THS status the last
        half year or are honorary members. New members that
        joined the last year are also considered active.

        Inactive accounts are filtered out, we do not look at the
        date_parted field because we assume is_active should be
        false for these users.
        """
        t = datetime.now()

        return queryset.filter(
            Q(payed_year__gte=t.year)
            | Q(honorary_member__exact=True)
            | Q(date_joined__gte=t - timedelta(days=365))
            | self.ths_member_claimed()
        )

    def recent_member(self, request, queryset):
        """
        List members that recently where members. Members that
        has a parted date and are active will be filtered out.
        """
        t = datetime.now()
        t2 = datetime.now() - timedelta(days=2 * 365)

        return (
            queryset.filter(
                Q(payed_year__gte=t2.year) | Q(ths_claimed_vt__gte=t2.year) | Q(ths_claimed_ht__gte=t2.year)
            )
            .exclude(date_parted__lte=datetime.now())
            .exclude(honorary_member__exact=True)
            .exclude(payed_year__gte=t.year)
            .exclude(date_joined__gte=t - timedelta(days=365))
            .exclude(self.ths_member_claimed())
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return self.active_member(request, queryset)
        if self.value() == "recent":
            return self.recent_member(request, queryset)


class MemberTHSStatus(admin.SimpleListFilter):
    t = datetime.now()
    is_vt = t.month <= 8
    title = f"THS Status VT{t.year}" if is_vt else f"THS Status HT{t.year}"

    parameter_name = "ths_status"

    def lookups(self, request, model_admin):
        return (
            ("claimed", "Claimed"),
            ("verified", "Verified"),
        )

    def queryset(self, request, queryset):
        t = datetime.now()

        if self.value() == "claimed":
            if self.is_vt:
                return queryset.filter(Q(ths_claimed_vt__exact=t.year))
            else:
                return queryset.filter(Q(ths_claimed_ht__exact=t.year))
        if self.value() == "verified":
            if self.is_vt:
                return queryset.filter(Q(ths_verified_vt__exact=t.year))
            else:
                return queryset.filter(Q(ths_verified_ht__exact=t.year))


class UserLoggedIn(admin.SimpleListFilter):
    title = "Has Logged In"
    parameter_name = "logged_in"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(~Q(last_login__exact=None))
        if self.value() == "no":
            return queryset.filter(Q(last_login__exact=None))


def export_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/json")
    serializers.serialize("json", queryset, stream=response)
    response["Content-Disposition"] = "attachment; filename=users.json"
    return response


export_json.short_description = "Export as JSON"


def export_kortexp(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=users.csv"

    writer = csv.writer(response)
    writer.writerow(["Name", "E-post", "KTH-ID", "Kortnummer", "Expireringsdatum"])
    for user in queryset:
        next_year = datetime.now().year + 1
        writer.writerow(
            [
                f"{user.first_name} {user.last_name}",
                user.email,
                user.kth_account,
                user.keycard_number,
                f"{next_year}-03-01 10:15",
            ]
        )

    return response


export_kortexp.short_description = "Export as CSV for kortexp"


def export_ths(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=users.csv"

    writer = csv.writer(response)
    writer.writerow(["Name", "E-post"])
    user_number = 1
    for user in queryset:
        user_name = f"{user.first_name} {user.last_name}" if not user.ths_name else user.ths_name
        user_email = user.email if not user.kth_account else f"{user.kth_account}@kth.se"
        if not user_email:
            user_email = f"{user.username}@stacken.kth.se"

        # Anonymize non-THS users, we use the claimed field so make sure
        # that one is up to date before this script is executed!
        if user.ths_claimed():
            writer.writerow([user_name, user_email])
        else:
            writer.writerow([f"Stacken User {user_number}", f"not-ths-member@stacken.kth.se"])

        user_number += 1

    return response


export_ths.short_description = "Export as CSV for THS"


class StackenUserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_active", "member_name")

    search_fields = ["username"]

    fieldsets = (
        (None, {"fields": ["username", "member"]}),
        ("Admin", {"fields": ("is_superuser", "is_staff", "is_active")}),
    )

    list_filter = [UserLoggedIn, "is_active"]

    def member_name(self, obj):
        if obj.member:
            link = reverse("admin:finger_member_change", args=[obj.member.id])
            name = f"{obj.member.first_name} {obj.member.last_name}"
            return mark_safe(f'<a href="{link}">{name}</a>')
        return None

    member_name.admin_order_field = "member_name"
    member_name.short_description = "Member"


class StackenMemberAdmin(admin.ModelAdmin):
    list_display = (
        "get_full_name",
        "last_member",
        "is_member",
        "ths_claimed",
        "ths_verified",
        "support_member",
    )

    search_fields = ("first_name", "last_name", "ths_name", "kth_account", "email")

    list_filter = (
        MemberListFilter,
        "support_member",
        "honorary_member",
        MemberTHSStatus,
        "has_key",
    )

    actions = (export_json, export_kortexp, export_ths, "send_email")

    fieldsets = (
        (None, {"fields": ("title", "first_name", "last_name", "email", "address", "phone", "comments")}),
        (
            "Medlemsstatus",
            {
                "fields": (
                    "payed_year",
                    ("ths_verified_vt", "ths_verified_ht"),
                    ("date_joined", "date_parted"),
                    ("honorary_member", "support_member", "has_signed"),
                )
            },
        ),
        ("Access", {"fields": ("has_key", "keycard_number")}),
        ("Kåren", {"fields": ("ths_name", ("ths_claimed_vt", "ths_claimed_ht"), "kth_account")}),
    )

    def send_email(self, request, queryset):
        if "apply" in request.POST:
            for member in queryset:
                emails = member.get_emails()
                sender_name = request.user.member.get_full_name()
                sender_email = f"{request.user.username}@stacken.kth.se"
                if emails:
                    mail.send(
                        emails,
                        sender=f"Datorföreningen Stacken via {sender_name} <{sender_email}>",
                        template=request.POST["template"],
                        context={"member": member},
                    )
            self.message_user(request, "E-Mails queued!")
            return HttpResponseRedirect(request.get_full_path())
        else:
            return render(
                request,
                "admin/send_email_confirmation.html",
                context={"members": queryset, "templates": EmailTemplate.objects.all()},
            )

    send_email.short_description = "Send E-Mail"


admin.site.register(User, StackenUserAdmin)
admin.site.register(Member, StackenMemberAdmin)
