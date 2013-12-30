from django.conf.urls import patterns, include, url
from django.conf import settings
PROJECT_ROOTDIR = getattr(settings, "PROJECT_ROOTDIR", "")
ENABLE_ADMIN = getattr(settings, "ENABLE_ADMIN", None)


from django.contrib import admin
admin.autodiscover()




if ENABLE_ADMIN:
	urlpatterns = patterns('',
		(r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'%s/media/' % (PROJECT_ROOTDIR), 'show_indexes': True}),
	    (r'admin/', include(admin.site.urls)),
	    url(r'^$', 'xxx.www.views.index', name='home'),
	    (r'^(?P<path>[-\w]+)/(?P<filtername>[\w -]+)', 'xxx.www.views.index'),
	    (r'^(?P<path>[-\w]+)','xxx.www.views.index'),
	)
else:
	urlpatterns = patterns('',
		(r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'%s/media/' % (PROJECT_ROOTDIR), 'show_indexes': True}),
	    
	    url(r'^$', 'xxx.www.views.index', name='home'),
	    (r'^(?P<path>[-\w]+)/(?P<filtername>[\w -]+)', 'xxx.www.views.index'),
	    (r'^(?P<path>[-\w]+)','xxx.www.views.index'),
	)
	