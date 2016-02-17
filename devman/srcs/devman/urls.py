from django.conf.urls import *
from django.views.static import serve
from devman.settings import STATIC_PATH, MEDIA_ROOT
from devman.jsonpage import JsonPage
from devman.dmroot.views import DMAuthView
from django.views.decorators.csrf import csrf_exempt

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^i18n/', include('django.conf.urls.i18n')), 
                       (r'^mymedia/(?P<path>.*)$', serve, { 'document_root': MEDIA_ROOT}),
                       (r'^incs/(?P<path>.*)$', serve, { 'document_root': STATIC_PATH }),
                       (r'^auth$', csrf_exempt(DMAuthView)),
                       (r'^.*$', JsonPage)
                       
                       
    # Example:
    # (r'^devman/', include('devman.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
