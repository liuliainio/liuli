from django.conf.urls.defaults import patterns, include, url
from estoreservice.api.views.app import share_app_download
from estoreservice.views import feedback

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'estoreservice.views.home', name='home'),
                       # url(r'^estoreservice/', include('estoreservice.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       #url(r'^admin/', include(admin.site.urls)),
                       url(r'^api/', include('estoreservice.api.urls')),
                       url(r'^openapi/',
                           include('estoreservice.openapi.urls')),
                       url(r'^share/(\d+)', share_app_download),
                       url(r'^feedback/(?P<types>\w+)', feedback),

                       url(r'^feedback', feedback),
                       )
