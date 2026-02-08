from api.views import *
from django.urls import path

urlpatterns = [
    path('write/', api_write_note, name='api_write_note'),
]