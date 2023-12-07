from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.utils import timezone
import re
from dateutil import parser
from datetime import datetime
from datetime import timedelta


class MemberManager(models.Manager):
    def is_valid_user(self, user):
        username = user.get("användarnamn")

        # finger.json contains some invalid data, some is fixable and some
        # is not. We have for exampele users that has the same username
        # registered. This will read a flag that ignores the username by
        # invalidating the username.
        if "username" in user.get("fingerweb_ignore", []):
            return False

        return username and re.match(r"^[a-z]+$", username) and username != "stacken"

    def list_to_str(self, the_list):
        return ", ".join(filter(None, the_list))

    def has_signed_contract(self, username):
        if self.is_valid_user({"användarnamn": username}):
            return not "(" in username
        else:
            return False

    def update_data(self, data):
        """
        Take an iterable of user data (the result of parsing finger.json),
        and create and/or update users accordingly.
        """

        for user in data:
            fields = {}

            # I see no point to keep _both_ values in separate fields. No script
            # uses them, they are only for human consumption. Make the list unique.
            fields["phone"] = self.list_to_str(list(set([user.get("arbtelefon"), user.get("hemtelefon")])))

            # Various information in the commens field, this contains possible
            # useful infomation for the future. But it's intended for human
            # consumption and the information is not that usable these days.
            fields["comments"] = self.list_to_str(
                [
                    user.get("avdelning"),
                    user.get("distrubution"),
                    user.get("organisation"),
                    user.get("status"),
                    user.get("syssel"),
                    user.get("comment"),
                    "Medlemmen är utesluten" if user.get("Utesluten") else "",
                ]
            )

            # Unless we have noted the address as incorrect, add the information
            # to the address field.
            if not user.get("Fel_adress"):
                fields["address"] = self.list_to_str(
                    [
                        "c/o " + user.get("c/o") if user.get("c/o") else "",
                        user.get("gatuadress"),
                        user.get("postadress"),
                        user.get("land"),
                    ]
                )

            # Because the user can choose to pay only for half the year we need to
            # verify THS members twice a year. In the old system we only noted what
            # year we checked the membership status.
            if datetime.now().month <= 8:
                fields["ths_claimed_vt"] = user.get("THS-studerande")
                fields["ths_verified_vt"] = user.get("THS-studerande")
            else:
                fields["ths_claimed_ht"] = user.get("THS-studerande")
                fields["ths_verified_ht"] = user.get("THS-studerande")

            # Various simple fields that do not need that much comments...
            fields["title"] = user.get("titel")
            fields["first_name"] = user.get("förnamn")
            fields["last_name"] = user.get("efternamn")
            fields["payed_year"] = user.get("betalt")
            fields["has_key"] = user.get("Hallnyckel", False)
            fields["support_member"] = user.get("stödmedlem", False)
            fields["honorary_member"] = user.get("Hedersmedlem", False)
            fields["keycard_number"] = user.get("kortnr")
            fields["date_joined"] = parse_date(user.get("inträdesdatum", "1970-01-01"))
            fields["identifier"] = user.get("fingerweb_identifier")

            # These fields are mainly here to make our verifications easier. Both with new
            # members but also when we talk with THS. The field ths_name is intended to be
            # used insted of first_ and last_name when we talk with THS. This can be useful
            # if the name in Stackens systems does not match what THS has on file.
            fields["ths_name"] = user.get("THS-namn")
            fields["kth_account"] = user.get("KTH-konto")

            # If the user has a kth.se-email address, assume the user part is the KTH account name
            if user.get("mailadress") and "@" in user.get("mailadress") and not user.get("KTH-konto"):
                email_fields = user.get("mailadress").split("@")
                if email_fields[1] == "kth.se":
                    fields["kth_account"] = email_fields[0]

            # For users that do not have an email address try to construct one with the
            # information we have on file.
            if user.get("mailadress"):
                fields["email"] = user.get("mailadress")
            else:
                kthname = user.get("KTH-konto")
                if kthname:
                    fields["email"] = kthname + "@kth.se"
                elif self.is_valid_user(user):
                    username = user.get("användarnamn")
                    fields["email"] = username + "@stacken.kth.se"

            # For users that have left the club. Set a parted date and invalidate contract
            if user.get("utträdesdatum"):
                fields["date_parted"] = parse_date(user.get("utträdesdatum"))
            else:
                fields["date_parted"] = None

            # Assume that users with active accounts have signed the contract
            # This is defined with the lack there of parentheses around the
            # username in finger.json
            if self.has_signed_contract(user.get("användarnamn")):
                fields["has_signed"] = True
            else:
                fields["has_signed"] = False

            # Invalidate contract on users that have have parted
            if user.get("Utesluten") or user.get("Slutat"):
                fields["has_signed"] = False

            # We need to uniqily identify a member in finger.json and map it to Member.
            # Use the special key fingerweb_identifier if found in finger.json, if not
            # found use the username.
            #
            # We have members without identifier and usernames, for these use the
            # following fallbacks:
            # - User provided email address
            # - Stacken email adress (will be generated from the username (if it's exists))
            # - First and last name
            #
            # If the above causes conflicts, add and fingerweb_identifier key to the member.
            if fields["identifier"]:
                member, _ = self.update_or_create(identifier__exact=fields["identifier"], defaults=fields)
            else:
                try:
                    user_from_db = User.objects.get(username=user.get("användarnamn"))
                except User.DoesNotExist:
                    user_from_db = User.objects.get(member__kth_account=fields["kth_account"])
                except User.DoesNotExist:
                    user_from_db = None

                if self.is_valid_user(user) and user_from_db:
                    member, _ = self.update_or_create(id=user_from_db.id, defaults=fields)
                elif "@" in fields.get("email", ""):
                    member, _ = self.update_or_create(email__exact=fields["email"], defaults=fields)
                else:
                    member, _ = self.update_or_create(
                        first_name__exact=fields["first_name"], last_name__exact=fields["last_name"], defaults=fields
                    )

            # Create and/or update an account for the member
            if fields.get("has_signed") and self.is_valid_user(user):
                user_fields = {
                    "member": member,
                    "date_joined": fields.get("date_joined"),
                }
                User.objects.update_or_create(username=user.get("användarnamn"), defaults=user_fields)


class Member(models.Model):
    first_name = models.CharField(max_length=30, null=True, default=None)
    last_name = models.CharField(max_length=150, null=True, default=None)
    email = models.CharField(max_length=254, null=True, default=None)
    date_joined = models.DateTimeField(null=True, default=None)
    payed_year = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Paid Year", help_text="The year the member has valid paid membership to."
    )
    ths_verified_vt = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="THS Verified Member VT",
        help_text="The member is verified to be a THS member for the fist half of the specified year.",
    )
    ths_verified_ht = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="THS Verified Member HT",
        help_text="The member is verified to be a THS member for the second half of the specified year.",
    )
    ths_claimed_vt = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="THS Claimed Member VT",
        help_text="The member has claimed to be a THS member for the fist half of the specified year.",
    )
    ths_claimed_ht = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="THS Claimed Member HT",
        help_text="The member has claimed to be a THS member for the second half of the specified year.",
    )
    phone = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Phone",
        help_text="One or several phone numbers to the member.",
    )
    comments = models.TextField(
        null=True, blank=True, verbose_name="Comments", help_text="One or more comments about the member."
    )
    address = models.TextField(null=True, blank=True, verbose_name="Address", help_text="The members address.")
    has_key = models.BooleanField(
        default=False, verbose_name="Has a Key", help_text="If the member has a key to the computer hall."
    )
    honorary_member = models.BooleanField(
        default=False, verbose_name="Honorary Member", help_text="If the member is a honorary member."
    )
    support_member = models.BooleanField(
        default=False,
        verbose_name="Support Member",
        help_text="The memeber is an support member, the member has no voting rights.",
    )
    keycard_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Keycard Number",
        help_text="The number of KTH's keycard, used by us to grant members access to the clubroom.",
    )
    kth_account = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="KTH account",
        help_text="The KTH accound name, useful when validating THS membership status.",
    )
    ths_name = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="THS Name",
        help_text="If the member is known by some other name in THS systems, this will override the name when we validates THS membership status.",
    )
    title = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Title", help_text="An optional title to the member."
    )
    date_parted = models.DateTimeField(
        null=True, blank=True, verbose_name="Date parted", help_text="The date of when a member left the club."
    )
    has_signed = models.BooleanField(
        default=False,
        verbose_name="Has signed the contract",
        help_text="The user has signed the contract, account access is allowed.",
    )
    identifier = models.CharField(
        max_length=32,
        default=None,
        null=True,
        verbose_name="A unique identifier",
        help_text="A unique identifier used to map a fingerweb user to this entry.",
    )

    objects = MemberManager()

    def is_member(self):
        """
        Return status if the user is considered an active member. If the user has
        a parted date, has not paid or verified THS membership (unless a new member)
        this year, consider the user not a member.
        """

        if self.has_parted():
            return False

        t = timezone.now()
        if ((self.last_member(format=2) + 1) >= t.year) or (t - timedelta(days=365) < self.date_joined):
            return True
        else:
            return False

    is_member.boolean = True

    def ths_claimed(self):
        """
        The user is a THS member
        """
        t = datetime.now()
        if t.month <= 8 and self.ths_claimed_vt:
            return self.ths_claimed_vt >= t.year
        elif self.ths_claimed_ht:
            return self.ths_claimed_ht >= t.year
        return False

    ths_claimed.boolean = True

    def ths_verified(self):
        """
        The user is a THS verified member
        """
        t = datetime.now()
        if t.month <= 8 and self.ths_verified_vt:
            return self.ths_verified_vt >= t.year
        elif self.ths_verified_ht:
            return self.ths_verified_ht >= t.year
        return False

    ths_verified.boolean = True

    def has_parted(self):
        """
        Checks if the user has parted or not from the club.
        TODO: Also check that the date is in the past
        """
        return self.date_parted

    def last_member(self, format=1):
        """
        Calculate last time this member was a member. Return a nice year from the
        middle ages if the information is missing in the database. Honorary members
        do not need to pay a member fee so they are considered members until they
        leave.
        """

        bucket = [1337]
        bucket.append(self.payed_year)
        bucket.append(self.ths_claimed_ht)
        bucket.append(self.ths_claimed_vt)
        bucket.append(self.date_joined.year)
        if self.honorary_member:
            if self.has_parted():
                bucket.append(self.date_parted.year)
            else:
                bucket.append(timezone.now().year)

        r = max([b for b in bucket if b])
        if format == 2:
            return r
        return str(r)

    def is_inactive(self):
        return datetime.now().year > (self.last_member(format=2) + 1)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    get_full_name.short_description = "Full Name"

    def joined_years_ago(self):
        return timezone.now().year - self.date_joined.year

    def get_emails(self):
        ret = []
        if self.email:
            ret.append(f"{self.get_full_name()} <{self.email}>")
        user = User.objects.filter(member=self.id)
        if user and user.count() < 2:
            ret.append(f"{self.get_full_name()} <{user[0].username}@stacken.kth.se>")
        return list(set(ret))

    def __repr__(self):
        return f"<Member: {self.get_full_name()} ({self.pk})>"

    def __str__(self):
        return f"{self.get_full_name()} (id: {self.pk})"


def parse_date(datestr):
    if datestr:
        return parser.parse("%s 12:00:00 CET" % datestr)
    else:
        return None


class User(AbstractUser):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField()
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, default=None)

    objects = UserManager()

    @property
    def email(self):
        if self.member.email:
            return self.member.email
        else:
            return "%s@stacken.kth.se" % self.username

    def __repr__(self):
        return f"<User: {self.username} ({self.pk})>"

    def __str__(self):
        return f"{self.username} (id: {self.pk})"
