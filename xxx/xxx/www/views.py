import os
from django.shortcuts import render_to_response, get_object_or_404, render, Http404
from models import Website, WebManager
from django.conf import settings

TEMPLATE_PATH = getattr(settings, "TEMPLATE_PATH", None)
def index(request, **kwargs):
    """
    Handle the index.
    web becomes a dictionary containing a 'context' key
    which will be returned to the template
    """
    path, filtername = kwargs.get('path'), kwargs.get('filtername')
    web = Website.objects.handle_request(request, path, filtername)
    if not web:
        raise Http404
    template = None
    if TEMPLATE_PATH:
        dirs = "%s/domains/%s/%s" % (TEMPLATE_PATH,
                                    web.get('website').domain,
                                    web.get('page').template_filename)
        if os.path.exists(dirs):
            template = dirs
    if not template:
        raise Exception('No template has been found')
    print web.get('context')
    return render(request, template, web.get('context'))


