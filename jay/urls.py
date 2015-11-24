"""jay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.views.generic import TemplateView

from . import demo_urls
from votes import urls as votes_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name="base/base.html")),
    url(r'^demo/', include(demo_urls)),

    url(r'^(?P<system_name>[\w-]+)/', include(votes_urls, namespace='votes')),

    # Legal things
    url(r'^imprint/$', TemplateView.as_view(template_name="base/imprint.html"), name="imprint"),
    url(r'^privacy/$', TemplateView.as_view(template_name="base/privacy.html"), name="privacy"),

    url(r'^login/', auth_views.login, {'template_name': 'auth/login.html'}),
    url(r'^logout/', auth_views.logout, {'template_name': 'auth/logout.html'}),
]
