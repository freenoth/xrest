"""xrest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views


app_name = 'api'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^files/$', views.files, name='files'),
    url(r'^files/(?P<pk>[\d]+)/$', views.file_detail, name='file_detail'),
    url(r'^files/(?P<pk>[\d]+)/meta/$', views.file_meta, name='file_meta'),
]
