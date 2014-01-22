import os
import sys
import site

path = '/home/sipit/rawdogger/djrawdogger/xxx'
site.addsitedir('/home/sipit/envs/sciweb/lib/python2.7/site-packages')
sys.path.append(path)
site.addsitedir('/home/sipit/envs/sciweb/lib/python2.7/site-packages')
sys.path.append('/home/sipit/rawdogger/djrawdogger/xxx')
sys.path.append('/home/sipit/rawdogger/djrawdogger/xxx/xxx')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

activate_env=os.path.expanduser('/home/sipit/envs/sciweb/bin/activate_this.py')
execfile(activate_env, dict(__file__=activate_env))
	
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
