from django.conf.urls.defaults import patterns, url

# need to add name for each url
urlpatterns = patterns('estoreoperation.analysis.views',
    url(r'^reporting', 'reporting_data'),
    url(r'^get_choices', 'get_choices'),
    url(r'^loadfile/data.csv', 'loadfile'),
    url(r'^loadfile/data.xls', 'loadfile'),
    url(r'^page/reporting/(?P<name>[a-z_]+)', 'reporting_chart_page', name="reporting_chart"),
    url(r'^list_analysis', 'export_list_analysis', name="export_list"),
    url(r'^file_analysis', 'export_file_analysis', name="export_file"),
)
