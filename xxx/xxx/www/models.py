from datetime import datetime
from django.db import models

class Website(models.Model):
    """
    We need a website to serve.
    """
    YN = ('y','y',),('n','n'),)
    domain = models.CharField(max_length=50)
    objects = WebManager()
    use_category = models.CharField(max_length=2,
                                    choices=YN)
    category = models.ForeignKey('Category', blank=True, null=True)
    

class CategoryManager(models.Manager):
    @classmethod
    def sync_with_tags(self):
        """Try to sync with models in xxxgalleries app."""
        try:
            from xxxgalleries.models import Tags as _tags
            for i in _tags.objects.all():
                try:
                    return Category.objects.get(name=i)
                except Category.DoesNotExist:
                    c = Category(name=i)
                    c.save()
        except ImportError:
            return None

class Category(models.Model):
    """
    Category to bind a website to
    """
    name = models.CharField(max_length=50)

class WebsitePage(models.Model):
    """
    Website pages to serve.
    """
    page = models.CharField(max_length=50)
    website = models.ForeignKey('Website')

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

class WebManager(models.Manager):
    @classmethod
    def handle_request(self, request, path=None, value=None):
        domain = self.get_meta_domain(request)
        try:
            website = Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            # return an empty context
            return {'context': {}}
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
