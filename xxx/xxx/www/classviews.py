"""
Set the static class views for admin functionality.
"""
import logging
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from models import Website, WebsitePage
from forms import WebsiteForm, WebsitePageForm
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
LOG_ON = getattr(settings, "LOG_ON", False)
MODULES = getattr(settings, "MODULES", ())
TRACK_IT = getattr(settings, "TRACK_IT", "")
try:
    from sciweb_tracker.models import *
except ImportError:
    TRACK_IT = False

class UpdateInstanceView(UpdateView):
    """Todo:
    update providers and banners classes
    to update views to use base UpdateInstanceView
    """
    def get_context_data(self, **kwargs):
        context = super(UpdateInstanceView, self).get_context_data(**kwargs)
        context['extmodules'] = MODULES
        return context
        
    def form_valid(self, form):
        self.object = form.save(commit=False)
        clean = form.cleaned_data
        for k, v in clean.items():
            setattr(self.object, k, v)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())



"""
class AdminIndexView(StaffuserRequiredMixin, TemplateView):
    # the admin index base view
    template_name = "www/admin-index.html"

"""
class BaseListView(ListView):
    def get_context_data(self, **kwargs):
        context = super(BaseListView, self).get_context_data(**kwargs)
        context['extmodules'] = MODULES
        return context

class BaseCreateView(CreateView):
    def get_context_data(self, **kwargs):
        context = super(BaseCreateView, self).get_context_data(**kwargs)
        context['extmodules'] = MODULES
        return context

class BaseDetailView(DetailView):
    """
    Base Detail Page View.
    """
    #queryset = Website.objects.all()

    def get_context_data(self, **kwargs):
        context = super(BaseDetailView, self).get_context_data(**kwargs)
        context['extmodules'] = MODULES
        return context


# Websites
class WebsiteView(StaffuserRequiredMixin, BaseListView):
    """
    Shows the list of websites.
    """
    model = Website

class CreateWebsite(StaffuserRequiredMixin, BaseCreateView):
    """
    Create a new Website.
    """
    model = Website

class UpdateWebsite(StaffuserRequiredMixin, UpdateInstanceView):
    """
    Updates a website.
    """
    model = Website
    form_class = WebsiteForm
    template_name = 'www/website_update.html'
    def get_object(self, queryset=None):
        obj = Website.objects.get(id=self.kwargs['pk'])
        return obj
    
class WebsiteDetailView(StaffuserRequiredMixin, BaseDetailView):
    """
    Website Detail Page View.
    """
    queryset = Website.objects.all()
    def get_object(self, **kwargs):
        obj = super(WebsiteDetailView, self).get_object(**kwargs)
        return obj


# Website Pages
class WebsitePageView(StaffuserRequiredMixin, BaseListView):
    """
    Shows a list of the website-pages.
    """
    model = WebsitePage

class CreateWebsitePage(StaffuserRequiredMixin, BaseCreateView):
    """
    Create a website-page.
    """
    model = WebsitePage

class UpdateWebsitePage(StaffuserRequiredMixin, UpdateInstanceView):
    """
    Updates a website page.
    """
    model = WebsitePage
    form_class = WebsitePageForm
    template_name = "www/websitepage_update.html"
    def get_object(self, queryset=None):
        obj = WebsitePage.objects.get(id=self.kwargs['pk'])
        return obj
    
class WebsitePageDetailView(StaffuserRequiredMixin, BaseDetailView):
    """
    Website-page detail view.
    """
    queryset = WebsitePage.objects.all()
    def get_object(self, **kwargs):
        obj = super(WebsitePageDetailView, self).get_object(**kwargs)
        return obj
    def get_context_data(self, **kwargs):
        context = super(WebsitePageDetailView, self).get_context_data(**kwargs)
        context['extmodules'] = MODULES
        if TRACK_IT:
            obj = context.get('object')
            context['uniques'] = Tracking.objects.get_uniques(domain=obj.website.domain)
            context['entrances'] = Tracking.objects.get_entrances(domain=obj.website.domain)
            context['pageviews'] = Tracking.objects.get_pageviews(domain=obj.website.domain)
            context['tracking'] = Tracking.objects.filter(domain=obj.website.domain,
                    action='view', path=obj.page, pageid=obj.pk)[:10]
        return context




