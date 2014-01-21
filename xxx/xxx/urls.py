from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.auth.views import login, logout

PROJECT_ROOTDIR = getattr(settings, "PROJECT_ROOTDIR", "")
ENABLE_ADMIN = getattr(settings, "ENABLE_ADMIN", None)
STAFF_URL = getattr(settings, "STAFF_URL", None)
ADMIN_URL = getattr(settings, "ADMIN_URL", None)


from django.contrib import admin
admin.autodiscover()

if ENABLE_ADMIN:
	urlpatterns = patterns('',
		(r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'%s/media/' % (PROJECT_ROOTDIR), 'show_indexes': True}),
        (r'%s/' % STAFF_URL, include('www.urls')),
	    (r'%s/' % ADMIN_URL, include(admin.site.urls)),
	    (r'logout', logout),
	    (r'accounts/login/$', login),
	    (r'login/$', login),

	    url(r'^$', 'xxx.www.views.index', name='home'),
	    (r'^(?P<path>[-\w]+)/(?P<filtername>[\w -]+)', 'xxx.www.views.index'),
	    (r'^(?P<path>[-\w]+)','xxx.www.views.index'),
	    
	)
else:
	urlpatterns = patterns('',
		(r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'%s/media/' % (PROJECT_ROOTDIR), 'show_indexes': True}),
	    (r'logout', logout),
	    (r'accounts/login/$', login),
	    (r'login/$', login),	

	    url(r'^$', 'xxx.www.views.index', name='home'),
	    (r'^(?P<path>[-\w]+)/(?P<filtername>[\w -]+)', 'xxx.www.views.index'),
	    (r'^(?P<path>[-\w]+)','xxx.www.views.index'),
	    
	)
	