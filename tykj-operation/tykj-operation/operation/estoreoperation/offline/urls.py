from django.conf.urls.defaults import patterns, url


# need to add name for each url
urlpatterns = patterns('estoreoperation.offline.views',
    url(r'^get_list', 'get_list'),
    url(r'^quick_offline', 'quick_offline'),
)
