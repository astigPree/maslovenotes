from frontend.views import *
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path('', HomePage, name='HomePage'),   
    path('robots.txt', RobotsTxt, name='RobotsTxt'),
    path('sitemap.xml', SitemapXml, name='SitemapXml'),
    path('favicon.ico', RedirectView.as_view(url='/static/assets/favicon.ico', permanent=True), name='Favicon'),
    path('notes/<str:pk>/', ViewerPage, name='ViewerPage'),
    path('write/', WritePage, name='WritePage'),
]
