from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

hidden_urls = getattr(settings, "hidden_urls", None)

urlpatterns = patterns('',
    (r'admin/', include(admin.site.urls)),
    url(r'^$', 'xxx.www.views.index', name='home'),
    (r'^(?P<path>[-\w]+)/(?P<filtername>[\w -]+)', 'xxx.www.views.index'),
    (r'^(?P<path>[-\w]+)','xxx.www.views.index'),
)
if hidden_urls:
    urlpatterns += hidden_urls
