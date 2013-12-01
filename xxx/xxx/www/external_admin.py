from django.contrib.contenttypes.models import ContentType
from django.contrib import admin

class GalleryAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'content', 'gallery_type',
                    'media_folder', 'hosted_jump_link', 'filter_name']
    list_filter = ('provider', 'content', 'gallery_type',)

class TagsAdmin(admin.ModelAdmin):
    list_display = ['name']

class ProvidersAdmin(admin.ModelAdmin):
    list_display = ['name']

class BannersAdmin(admin.ModelAdmin):
    list_display = ['name', 'ratio', 'width', 'height', 'jumplink']
    list_filter = ('ratio',)

# create the models from content type
try:
    _gallery = ContentType.objects.get(name='Gallery')
    Gallery = _gallery.model_class()
    admin.site.register(Gallery, GalleryAdmin)
except ContentType.DoesNotExist:
    pass

try:
    _tags = ContentType.objects.get(name='Tags')
    Tags = _tags.model_class()
    admin.site.register(Tags, TagsAdmin)
except ContentType.DoesNotExist:
    pass

try:
    _banners = ContentType.objects.get(name='Banners')
    Banners = _banners.model_class()
    admin.site.register(Banners, BannersAdmin)
except ContentType.DoesNotExist:
    pass

try:
    _providers = ContentType.objects.get(name='Providers')
    Providers = _providers.model_class()
    admin.site.register(Providers, ProvidersAdmin)
except ContentType.DoesNotExist:
    pass
