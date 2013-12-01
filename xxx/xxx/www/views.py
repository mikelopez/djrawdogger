from django.shortcuts import render_to_response, get_object_or_404, render
from models import Website, WebManager

def index(request, link, filtername):
    """
    Handle the index.
    web becomes a dictionary containing a 'context' key
    which will be returned to the template
    """
    web = Website.objects.handle_request(request, link, filtername)
    template = "index.html"
    return render(request, template, web.get('context'))


