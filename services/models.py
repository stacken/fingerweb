from django.db import models
from finger.models import User

class Service(models.Model):
    name = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return self.name

    def account_for(self, user):
        return None

class ServiceUser(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret = models.TextField()
