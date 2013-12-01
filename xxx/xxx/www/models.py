from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

# static urls checked first for static filters on query
URLS = [getattr(settings, "BROWSE_URL", None),
        getattr(settings, "PIC_URL", None),
        getattr(settings, "VIDS_URL", None)]
TEMPLATE_PATH = getattr(settings, "TEMPLATE_PATH", "")

class WebManager(models.Manager):
    filters = {}

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
            Gallery = self.gallery_model()
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
        Gallery = self.gallery_model()

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
        Gallery = self.gallery_model()
        if value:
            try:
                return Gallery.objects.get(pk=int(value), content='video')
            except Gallery.DoesNotExist:
                try:
                    return Gallery.objects.get(name=str(value), content='video')
                except (ValueError, Gallery.DoesNotExist):
                    return None
        return Gallery.objects.filter(content='video')

    @classmethod
    def handle_request(self, request, path=None, value=None):
        """Handles the main request."""
        domain = self.get_meta_domain(request)
        website, page = get_website_and_page(domain, path)

        context = {'context': {'data': None}}
        fetch = getattr(page, 'get_data', False)
        if get_content:
            if path in URLS:
                if value:
                    self.filters['value'] = value
                try:
                    context.get('context')['data'] = getattr(self, path, None)
                except AttributeError:
                    pass
                # always force any page to its categories that are set
            else:
                Gallery = self.gallery_model()
                context.get('context')['data'] = Gallery.objects.all()
            categories = page.categories.all()
            if categories:
                qf = {'tags__in': categories}
                context.get('context')['data'].filter(**qf)
        context['template'] = self.get_template(page)
        return context

    def get_template(self, page):
        """
        If template does is none, raise PageProcessor exception
        """
        template_filename = page.template
        searchpath = '%s/domains/%s/%s' % (TEMPLATE_PATH,
                                           page.website.domain,
                                           template_filename)
        # if custom domain doesnt exist
        if os.path.exists(searchpath):
            #self.logger.write('Custom path domains exists, using that template!')
            return searchpath
        else:
            #self.logger.write('NOT FOUND default template %s' % (searchpath))
            raise PageProcessorException('No Template Found %s' % (searchpath))


    def gallery_model(self):
        """Return the Gallery() model class from ext app"""
        try:
            g = ContentType.objects.get(name='gallery')
        except ContentType.DoesNotExist:
            return None
        return g.model_class()

    def get_website_and_page(self, domain, path):
        """Gets the website and page from request data"""
        try:
            website = Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            return {'context': {}}
        try:
            page = WebsitePage.objects.get(website=website, page=path)
        except WebsitePage.DoesNotExist:
            return {}


    def get_meta_domain(self, request):
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
        if logger:
            try:
                logger.info("utils.get_meta_domain: domain %s" % (domain_string))
            except:
                pass
        return domain_string.replace('http://', '').replace('www.','')


class Website(models.Model):
    """
    We need a website to serve.
    """
    YN = (('y','y',),('n','n'))
    domain = models.CharField(max_length=50)
    objects = WebManager()

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
    categories = models.ManyToManyField('Category')
    get_data = models.NullBooleanField(default=False)
    show_categories = models.NullBooleanField(default=False)
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

