from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload_json),
    path('mail_members', views.mail_members)
]
