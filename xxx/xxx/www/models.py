from datetime import datetime
from django.db import models

class Website(models.Model):
    """
    We need a website to serve.
    """
    domain = models.CharField(max_length=50)
    objects = WebManager()

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
    def handle_request(self, request):

