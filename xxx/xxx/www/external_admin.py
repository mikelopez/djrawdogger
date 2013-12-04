from django.contrib.contenttypes.models import ContentType
from django.contrib import admin

class GalleryAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'content', 'gallery_type',
                    'media_folder', 'hosted_jump_link', 'filter_name']
    list_filter = ('provider', 'content', 'gallery_type',)

class TagsAdmin(admin.ModelAdmin):
    list_display = ['name', 'cache_picgalleries_count', 'cache_vidgalleries_count',
                    'main_tag', 'model_tag', 'site_tag']
    list_filter = ('main_tag', 'model_tag', 'site_tag',)

class ProvidersAdmin(admin.ModelAdmin):
    list_display = ['name']

class BannersAdmin(admin.ModelAdmin):
    list_display = ['name', 'ratio', 'width', 'height', 'jumplink']
    list_filter = ('ratio',)

class PicTagFacesAdmin(admin.ModelAdmin):
    list_display = ['tag', 'gallery',]

class VidTagFacesAdmin(admin.ModelAdmin):
    list_display = ['tag', 'gallery',]

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

try:
    _ptagfaces = ContentType.objects.get(name='PicTagFaces')
    PicTagFaces = _ptagfaces.model_class()
    admin.site.register(PicTagFaces, PicTagFacesAdmin)
except ContentType.DoesNotExist:
    pass

try:
    _vtagfaces = ContentType.objects.get(name='VidTagFaces')
    VidTagFaces = _vtagfaces.model_class()
    admin.site.register(VidTagFaces, VidTagFacesAdmin)
except ContentType.DoesNotExist:
    pass