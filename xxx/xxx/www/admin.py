from django.contrib import admin
from models import Website, Category, WebsitePage

class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['domain', 'active', 'whitelabel', 'watermarked']

class WebsitePageAdmin(admin.ModelAdmin):
    list_display = ['website', 'page', 'get_categories',
                    'get_data', 'show_categories']
    list_filter = ('website',)

#class AnalyticsAdmin(admin.ModelAdmin):
#    list_display = ['website', 'page', 'count', 'ip', 'hitdate', 'ua']
#    list_filter = ('website',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Website, WebsiteAdmin)
admin.site.register(WebsitePage, WebsitePageAdmin)
#admin.site.register(Analytics, AnalyticsAdmin)
admin.site.register(Category, CategoryAdmin)

from external_admin import *


