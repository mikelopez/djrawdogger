from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from www.views import CreateWebsite, UpdateWebsite, WebsiteView, WebsiteDetailView, \
        CreateWebsitePage, UpdateWebsitePage, WebsitePageView, WebsitePageDetailView
        

PROJECT_ROOTDIR = getattr(settings, 'PROJECT_ROOTDIR', '')

urlpatterns = patterns('',

    url(r'^$', WebsiteView.as_view(), name="adminview"),
    
    url(r'^website/add', CreateWebsite.as_view(), name="website_add"),
    url(r'^website/update/(?P<pk>\d+)', UpdateWebsite.as_view(), name="update_website"),
    url(r'^website/(?P<pk>\d+)', WebsiteDetailView.as_view(), name="website_detail"),
    url(r'^website/', WebsiteView.as_view(), name="website_view"),

    url(r'^sitepage/add', CreateWebsitePage.as_view(), name="websitepage_add"),
    url(r'^sitepage/update/(?P<pk>\d+)', UpdateWebsitePage.as_view(), name="websitepage_update"),
    url(r'^sitepage/(?P<pk>\d+)', WebsitePageDetailView.as_view(), name="websitepage_detail"),
    url(r'^sitepage/', WebsitePageView.as_view(), name="websitepage_view"),

    #(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'%s/static/' % (PROJECT_ROOTDIR), 'show_indexes': True}),


)
