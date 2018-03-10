from django.db import models
from finger.models import User
from random import SystemRandom
import string

class Service(models.Model):
    name = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return self.name

    def account_for(self, user):
        return self.serviceuser_set.get(user=user)

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

class ServiceUser(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret = models.TextField()

def create_password(length):
    chars = 2*string.ascii_lowercase + string.ascii_letters + 3*string.digits
    rand = SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))
