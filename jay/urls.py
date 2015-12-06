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

from core.views import home

from votes import urls as votes_urls
from filters import urls as filters_urls
from settings import urls as settings_urls

urlpatterns = [
    # Home page
    url(r'^$', home, name="home"),

    # TODO: Remove these?
    url(r'^admin/', include(admin.site.urls)),

    # Static stuff
    url(r'^imprint/$', TemplateView.as_view(template_name="base/imprint.html"), name="imprint"),
    url(r'^privacy/$', TemplateView.as_view(template_name="base/privacy.html"), name="privacy"),

    # Help
    url(r'^help/filters/$', TemplateView.as_view(template_name="filters/filter_help.html"), name="filter_help"),

    # Authentication
    url(r'^login/', auth_views.login, {'template_name': 'auth/login.html'}, name="login"),
    url(r'^logout/', auth_views.logout, {'template_name': 'auth/logout.html', 'next_page':'home'}, name="logout"),

    # Sub-projects
    url(r'^filters/', include(filters_urls, namespace='filters')),
    url(r'^settings/', include(settings_urls, namespace='settings')),
    url(r'^(?P<system_name>[\w-]+)/', include(votes_urls, namespace='votes')),
]
