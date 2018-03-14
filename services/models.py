from django.db import models
from finger.models import User
from markdown import markdown
from random import SystemRandom
import string

class Service(models.Model):
    name = models.SlugField(db_index=True, unique=True)
    shortdesc = models.CharField(max_length=100, null=True)
    longdesc = models.TextField(null=True)

    def __str__(self):
        return self.name

    def description_html(self):
        return markdown(self.longdesc)

    def account_for(self, user):
        try:
            return self.serviceuser_set.get(user=user)
        except ServiceUser.DoesNotExist:
            return None

    def generate_password(self, user):
        new_password = create_password(18)
        print("Should generate key for %s on %s" % (user, self))
        obj, created = ServiceUser.objects.get_or_create(
            service=self,
            user=user,
            defaults = { 'secret': new_password }
        )
        if not created:
            obj.secret = new_password
            obj.save()
        return None

    def nr_users(self):
        return self.serviceuser_set.count()

class ServiceUser(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret = models.TextField()

def create_password(length):
    chars = 2*string.ascii_lowercase + string.ascii_letters + 3*string.digits
    rand = SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))
