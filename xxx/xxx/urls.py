from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

hidden_urls = getattr(settings, "hidden_urls", None)

urlpatterns = patterns('',
    url(r'^$', 'xxx.views.index', name='home'),
    (r'^(?P<linkname>[-\w]+)/(?P<filtername>[\w -]+)', 'xxx.views.index'),
    (r'^(?P<linkname>[-\w]+)','xxx.views.index'),
)
if hidden_urls:
    urlpatterns += hidden_urls
