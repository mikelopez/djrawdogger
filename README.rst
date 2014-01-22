Custom media content web controller.

Copy local_settings.py 
Replace any settings data in local_settings.py

.. code-block:: python

    from django.conf.urls import patterns, include, url

    ENABLE_ADMIN = True
    DEBUG = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'dbuser',                      # Or path to database file if using sqlite3.
            # The following settings are not used with sqlite3:
            'USER': 'dbname',
            'PASSWORD': 'passwd',
            'HOST': 'host',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': '',                      # Set to empty string for default.
        }
    }
    DATABASE_ENGINE = DATABASES.get('default').get('ENGINE')
    DATABASE_NAME = DATABASES.get('default').get('NAME')
    DATABASE_USER = DATABASES.get('default').get('USER')
    DATABASE_PASSWORD = DATABASES.get('default').get('PASSWORD')
    DATABASE_HOST = DATABASES.get('default').get('HOST')


    # static path to your external templates 
    TEMPLATE_PATH = '/template/custom/dir'

    SECRET_KEY = '*l&oe)!4lvg4)+vbihclhagmci=29=e(8^77&*nh9v2erq@r0s'

    INTERNAL_IPS = ('127.0.0.1','localhost',)

    # dev
    ALLOWED_HOSTS = ['*']

    #production
    ALLOWED_HOSTS = ['sites-allowed.com']

    # module URLS to show in base template navigation dropdown
    MODULES = (('http://some-outside-url.com', 'Tracking'),
               ('/some/internal/url/', 'Content'),
               ('/staff/website/', 'Mainweb'),)

    STAFF_URL = "custom-staff"
    ADMIN_URL = "custom-admin"
    # dev
    if DEBUG:
    	ALLOWED_HOSTS = ['*']
    else:
    	#production
    	ALLOWED_HOSTS = ['rawdogger.com', 'www.rawdogger.com']
    
    LOGIN_REDIRECT_URL = "/%s" % STAFF_URL


