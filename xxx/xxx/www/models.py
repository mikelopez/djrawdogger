import os
from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

# static urls checked first for static filters on query
URLS = [getattr(settings, "BROWSE_URL", None),
        getattr(settings, "PIC_URL", None),
        getattr(settings, "VIDS_URL", None)]
TEMPLATE_PATH = getattr(settings, "TEMPLATE_PATH", "")


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

    @property
    def browse(self):
        """
        Browse page.
        If value is in filters, search for categories.
        If not, return all content.
        """
        value = self.filters.get('value')
        if value:
            # search by a category name/id
            try:
                cat = Category.objects.get(pk=int(value))
            except (ValueError):
                try:
                    cat = Category.objects.get(name=str(value))
                except (ValueError, Category.DoesNotExist):
                    cat = None
            qfilter = {}
            if cat:
                tag_object = cat.get_tag_object()
                qfilter = {'tags_in': [tag_object]}
            Gallery = self.get_gallery_model()
            return Gallery.objects.filter(**qfilter)
        return None

    @property
    def pics(self):
        """
        Pics page
        This requires an ID/Name argument
        If none is passed, it returns all picture galleries.
        """
        value = self.filters.get('value')
        Gallery = self.get_gallery_model()

        if value:
            try:
                return Gallery.objects.get(pk=int(value), content='pic')
            except Gallery.DoesNotExist:
                try:
                    return Gallery.objects.get(name=str(value), content='pic')
                except (ValueError, Gallery.DoesNotExist):
                    return None
        return Gallery.objects.filter(content='pic')

    @property
    def vids(self):
        value = self.filters.get('value')
        Gallery = self.get_gallery_model()
        if value:
            try:
                return Gallery.objects.get(pk=int(value), content='video')
            except Gallery.DoesNotExist:
                try:
                    return Gallery.objects.get(name=str(value), content='video')
                except (ValueError, Gallery.DoesNotExist):
                    return None
        return Gallery.objects.filter(content='video')



class WebManager(models.Manager):
    """Web Manager HTTP request handler"""
    filters = {}

    @classmethod
    def get_data(path, value):
        content_class = ContentData()
        self.filters['value'] = value
        data = getattr(content_class, path, {})
        return data

    def handle_request(self, request, path, value):
        """Handles the main request."""
        if not path and not value:
            path = 'index'
        print path
        domain = get_meta_domain(request)
        website, page = self.get_website_and_page(domain, path)
        if not website or not page:
            return None
        context = {'context': {'data': None},
                   'website': website, 'page': page}
        fetch = getattr(page, 'get_data', False)
        if page.show_categories:
            Tags = Website.objects.gallery_model(name_override="tags")
            context['context']['categories'] = Tags.objects.all().order_by('name')

        if fetch:
            if path in URLS:
                try:
                    context.get('context')['data'] = Website.objects.get_data(path, value)
                except AttributeError:
                    pass
                # always force any page to its categories that are set
            else:
                Gallery = Website.objects.gallery_model()
                context.get('context')['data'] = Gallery.objects.all()
            categories = page.categories.all()
            if categories:
                qf = {'tags__in': categories}
                context.get('context')['data'].filter(**qf)
        context['template'] = get_template(page)
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
            return None, None
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
    objects = WebManager()
    def __str__(self):
        return str(self.domain)
    def __unicode__(self):
        return unicode(self.domain)

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
    categories = models.ManyToManyField('Category', blank=True, null=True)
    get_data = models.NullBooleanField(default=False)
    show_categories = models.NullBooleanField(default=False)
    template_filename = models.CharField(max_length=150, blank=True, null=True)
    @property
    def get_categories(self):
        c = ""
        for x in self.categories.all():
            c += "%s, " % (x.name)
        return c

class Analytics(models.Model):
    """
    Keep track of teh site analytics.
    """
    website = models.ForeignKey('Website')
    page = models.CharField(max_length=50)
    count = models.IntegerField(default=0)
    ip = models.CharField(max_length=19)
    hitdate = models.DateTimeField(default=datetime.now(),
                                   auto_now_add=True)
    ua = models.TextField(blank=True, null=True)

