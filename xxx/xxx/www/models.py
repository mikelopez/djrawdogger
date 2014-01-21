import os
import uuid
from datetime import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

# static urls checked first for static filters on query
URLS = [getattr(settings, "BROWSE_URL", None),
        getattr(settings, "PIC_URL", None),
        getattr(settings, "VIDS_URL", None),
        getattr(settings, "SHOW_URL", None)]
TEMPLATE_PATH = getattr(settings, "TEMPLATE_PATH", "")
TRACK_IT = getattr(settings, "TRACK_IT", "")
try:
    from sciweb_tracker.models import *
except ImportError:
    TRACK_IT = False


def get_meta_domain(request):
    """
    Return website object by http data - no mistakes 
    use this to get the domain name to search for a specific sitepage
    and website
    """
    try:
        sitename = request.get('HTTP_HOST')
    except AttributeError:
        sitename = None
    # if request.get returned None
    if not sitename:
        sitename = request.META.get('HTTP_HOST')
    domain_string = sitename.split(':')[0]
    if not domain_string:
        return None
    return domain_string.replace('http://', '').replace('www.','')

class ContentData(object):
    """
    Gets the content via a property
    """
    filters = {}
    def get_gallery_model(self):
        return Website.objects.gallery_model()

    def get_tag_model(self):
        """Get the tag model class and object from the external app."""
        try:
            _tags = ContentType.objects.get(name='tags')
            return _tags.model_class()
        except ContentType.DoesNotExist:
            return None


    @property
    def browse(self):
        """
        Browse page returns pics and video content
        If value is in filters, search for tag.
        If not, return all content.
        Returns {
            'tag': Tag object 
            'galleries': Galleries QuerySet
        }
        """
        value = self.filters.get('value')
        returns = {'category': None}
        Tags = self.get_tag_model()
        qfilter = {}
        if value:
            # search by a category name/id
            try:
                cat = Tags.objects.get(pk=int(value))
            except (Tags.DoesNotExist, ValueError):
                try:
                    cat = Tags.objects.get(name=str(value))
                except (ValueError, Tags.DoesNotExist):
                    cat = None
            if cat:
                qfilter = {'tags__in': [cat]}
                returns['category'] = cat

        Gallery = self.get_gallery_model()
        qfilter['content'] = 'pic'
        returns['pic_galleries'] = Gallery.objects.filter(**qfilter).order_by('?')
        qfilter['content'] = 'video'
        returns['video_galleries'] = Gallery.objects.filter(**qfilter).order_by('?')
        return returns

    @property 
    def showgallery(self):
        """Shows the gallery. Required value ID of the gallery"""
        value = self.filters.get('value')
        print "Run show gallery() with value %s" % value
        Gallery = self.get_gallery_model()
        returns = {}
        if value:
            try:
                returns['gallery'] = Gallery.objects.get(pk=int(value))
                return returns
            except (Gallery.DoesNotExist, ValueError):
                # additionally try to look up by name string
                try:
                    returns['gallery'] = Gallery.objects.get(filter_name=str(value))
                    return returns
                except (ValueError, Gallery.DoesNotExist):
                    return returns
        return returns

    @property
    def pics(self):
        """
        Pics page
        This requires an ID/Name argument
        If none is passed, it returns all picture galleries.
        """
        value = self.filters.get('value')
        Gallery = self.get_gallery_model()
        self.filters['content'] = 'pic'
        return self.browse


    @property
    def vids(self):
        """Videos page
        If id/name argument is passed, it filters by that category.
        """
        value = self.filters.get('value')
        Gallery = self.get_gallery_model()
        self.filters['content'] = 'video'
        return self.browse



class WebManager(models.Manager):
    """Web Manager HTTP request handler"""
    filters = {}

    def get_data(self, path, value):
        """Interface to content data class"""
        content_class = ContentData()
        content_class.filters['value'] = value
        print "Value is %s" % value
        data = getattr(content_class, path, {})
        return data

    def get_selected_categories(self, context, moc, mc, sc):
        """Sets the filtered categories into the context and returns.
        moc = Model categories/tags
        mc = Main categories/tags
        sc = Site categories/tags
        """
        if not mc and not moc and not sc:
            Tags = Website.objects.gallery_model(name_override="tags")
            context['context']['categories'] = Tags.objects.all().order_by('name')
        else:
            Tags = Website.objects.gallery_model(name_override="tags")
            if mc:
                context['context']['main_categories'] = []
                cntx = context['context']['main_categories'] = []
                thetags = Tags.objects.filter(main_tag=True).order_by('name')
            if moc:
                context['context']['model_categories'] = []
                cntx = context['context']['model_categories'] = []
                thetags = Tags.objects.filter(model_tag=True).order_by('name')
            if sc:
                context['context']['site_categories'] = []
                cntx = context['context']['site_categories'] = []
                thetags = Tags.objects.filter(site_tag=True).order_by('name')
            c = 0    
            for i in thetags:
                cntx.append({'name': i.name, 'id': i.id,
                             'cache_picgalleries_count': i.cache_picgalleries_count,
                             'cache_vidgalleries_count': i.cache_vidgalleries_count,
                             'thumbnail': i.get_pic_tag_thumb()})
                c += 1
        return context

    def handle_request(self, request, path, value):
        """Handles the main request."""
        if not path and not value:
            path = 'index'
        domain = get_meta_domain(request)
        website, page = self.get_website_and_page(domain, path)
        if website:
            if website.redirect_to:
                return {'redirect': website.redirect_to}
        if not website or not page:
            return None
        context = {'context': {'data': None,
                               'website': website, 'page': page}}
        fetch = getattr(page, 'get_data', False)

        # set the categories to the context
        if page.show_categories:
            moc, mc, sc = page.model_categories, \
                          page.main_categories, \
                          page.site_categories
            context =self.get_selected_categories(context, moc, mc, sc)

        # set the galleries/other data to the context
        if fetch:
            if path in URLS:
                try:
                    context.get('context')['data'] = Website.objects.get_data(path, value)
                except AttributeError:
                    pass
                # always force any page to its categories that are set
            else:
                Gallery = Website.objects.gallery_model()
                context.get('context')['picture_galleries'] = \
                            Gallery.objects.filter(content='pic').order_by('?')
                context.get('context')['video_galleries'] = \
                            Gallery.objects.filter(content='video').order_by('?')

            # set the category filter to data 
            categories = page.categories.all()
            if categories:
                qf = {'tags__in': categories}
                if context.get('context').get('data'):
                    try:
                        context.get('context').get('data').filter(**qf)
                    except AttributeError:
                        pass

        # done... get the template and return now
        context['template'] = get_template(page)
        # at the end, track results if set 
        if TRACK_IT:
            if not request.session.get('SID'):
                request.session['SID'] = uuid.uuid4()
            t = Tracking.objects.trackit(sid=request.session.get('SID'), 
                                            action='view', 
                                            name='default',
                                            domain=website.domain, 
                                            path=page.page,
                                            pageid=page.pk, 
                                            ipaddress=request.META.get('REMOTE_ADDR'), 
                                            ua=request.META.get('HTTP_USER_AGENT'))
        return context

    def get_website_and_page(self, domain, path):
        """Gets the website and page from request data"""
        try:
            website = Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            return None, None
        try:
            page = WebsitePage.objects.get(website=website, page=path)
        except WebsitePage.DoesNotExist:
            return website, None
        return website, page

    @classmethod
    def gallery_model(self, name_override=None):
        """Return the Gallery() model class from ext app"""
        try:
            if not name_override:
                g = ContentType.objects.get(name='gallery')
            else:
                g = ContentType.objects.get(name=name_override)
        except ContentType.DoesNotExist:
            return None
        return g.model_class()

def get_template(page):
    """
    If template does is none, raise PageProcessor exception
    """
    template_filename = page.template_filename
    searchpath = '%s/domains/%s/%s' % (TEMPLATE_PATH,
                                       page.website.domain,
                                       template_filename)
    # if custom domain doesnt exist
    if os.path.exists(searchpath):
        #self.logger.write('Custom path domains exists, using that template!')
        return searchpath
    else:
        #self.logger.write('NOT FOUND default template %s' % (searchpath))
        return None


class Website(models.Model):
    """
    We need a website to serve.
    """
    YN = (('y','y',),('n','n'))
    domain = models.CharField(max_length=50)
    active = models.NullBooleanField(default=False, null=True, blank=True)
    whitelabel = models.NullBooleanField(default=False, null=True, blank=True)
    watermarked = models.NullBooleanField(default=False, null=True, blank=True)
    redirect_to = models.TextField(blank=True, null=True)
    objects = WebManager()

    def __str__(self):
        return str(self.domain)
    def __unicode__(self):
        return unicode(self.domain)
    def has_pages(self):
        if self.websitepage_set.select_related().count() > 0:
            return True
        return False

    def get_absolute_url(self):
        return reverse('website_detail', kwargs={'pk': self.pk})



class CategoryManager(models.Manager):
    """Category Manager"""
    def get_tags_model_class(self):
        try:
            _tags = ContentType.objects.get(name='tags')
        except ContentType.DoesNotExist:
            return None
        return _tags.model_class()

    @classmethod
    def tag_model(self):
        return self.get_tags_model_class()

    @classmethod
    def sync_with_tags(self, full=False):
        """Make sure all Tags() exist in Categories()"""
        try:
            Tags = get_tags_model_class().model_class()
            for i in Tags.objects.all():
                try:
                    return Category.objects.get(name=i)
                except Category.DoesNotExist:
                    c = Category(name=i)
                    c.save()
        except ImportError:
            return None
        if full:
            self.backward_sync()

    def backward_sync(self):
        """Checks if the tags here exist in Categories"""
        try:
            Tags = get_tags_model_class().model_class()
            for i in Category.objects.all():
                try:
                    Tags.objects.get(name=i.name)
                except Tags.DoesNotExist:
                    i.delete()
        except ImportError:
            return None

class Category(models.Model):
    """
    Category to bind a website to
    """
    name = models.CharField(max_length=50)
    objects = CategoryManager()
    def get_tag_object(self):
        """Return the tag object whos name is same as self.name"""
        try:
            return Category.objects.tag_model().get(name=self.name)
        except:
            return None

class WebsitePage(models.Model):
    """
    Website pages to serve.
    Define any settings and filters here
    """
    page = models.CharField(max_length=50)
    website = models.ForeignKey('Website')
    title = models.CharField(max_length=150, blank=True, null=True)
    categories = models.ManyToManyField('Category', blank=True, null=True)
    get_data = models.NullBooleanField(default=False)
    show_categories = models.NullBooleanField(default=False)
    main_categories = models.NullBooleanField(default=False)
    site_categories = models.NullBooleanField(default=False)
    model_categories = models.NullBooleanField(default=False)
    template_filename = models.CharField(max_length=150, blank=True, null=True)
    footer_scripts = models.TextField(blank=True, null=True)
    @property
    def get_categories(self):
        c = ""
        for x in self.categories.all():
            c += "%s, " % (x.name)
        return c

    def get_absolute_url(self):
        return reverse('websitepage_detail', kwargs={'pk': self.pk})


