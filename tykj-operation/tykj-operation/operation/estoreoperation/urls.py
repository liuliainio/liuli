from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from ajax_select import urls as ajax_select_urls

from estorecore.admin.sites import custom_site
from estoreoperation.analysis import urls as analysis_urls
from estoreoperation.views import get_related_lookup_info, get_package_name, sync_applist_add, \
        get_app_detail, sync_tianyi_app, generate_verify_code, get_all_app_labels, clear_online_app

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('estoreoperation.locale.jsi18n',),
}

urlpatterns = patterns('',
    url(r'^admin/', include(custom_site.urls)),
    url(r'^analysis/', include(analysis_urls)),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^admin/get_related_lookup_info', get_related_lookup_info, name='get_related_lookup_info'),
    url(r'^admin/get_package_name', get_package_name, name='get_package_name'),
    url(r'^admin/sync_applist_add', sync_applist_add, name='sync_applist_add'),
    url(r'^admin/get_app_detail', get_app_detail),

    url(r'^api/sync.json', sync_tianyi_app, name='sync_tianyi_app'),
    url(r'^verify_code', generate_verify_code, name='generate_verify_code'),
    url(r'^get_app_labels', get_all_app_labels, name='get_all_app_labels'),
    url(r'^clear_app', clear_online_app, name='clear_online_app'),
)
