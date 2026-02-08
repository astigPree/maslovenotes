from frontend.views import *
from django.urls import path

urlpatterns = [
    path('', HomePage, name='HomePage'),   
    path('notes/<str:pk>/', ViewerPage, name='ViewerPage'),
    path('write/', WritePage, name='WritePage'),
]