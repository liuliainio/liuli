from django.utils.translation import ugettext_lazy as _
from estorecore.admin.sites import custom_site
from estorecore.admin import EntityModelAdmin
from estoreoperation.search.models import SearchKeyword,KeywordLocation
from django.core.urlresolvers import reverse


class SearchKeywordAdmin(EntityModelAdmin):
    list_editable = ('order', 'search_count', 'search_trend', 'published', 'review_status')
    list_display = ('order', 'keyword', 'search_count', 'search_trend', 'published', 'review_status', 'sync_status')
    list_display_links = ('keyword',)
    list_filter = ['sync_status', 'review_status', 'search_trend','published']
    list_per_page = 50
    search_fields = ['keyword']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('keyword', 'search_count', 'search_trend'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
        )

class KeywordLocationAdmin(EntityModelAdmin):
    list_editable = ('location', 'published', 'review_status')
    list_display = ('app_link', 'location', 'keyword', 'published', 'review_status', 'sync_status')
    list_display_links = ('keyword',)
    list_filter = ['sync_status', 'review_status']
    list_per_page = 50
    search_fields = ['keyword']
    ordering = ('order',)
    raw_id_fields = ('app',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('app','keyword', 'location'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )
    def app_link(self, obj):
        info = self.model._meta.app_label, self.model._meta.module_name
        return """<a href="/admin/app/application/%s/?rtn_url=%s" target="_blank"><strong>%s</strong></a>""" \
                % (obj.app.id, reverse('admin:%s_%s_changelist' % info), obj.app.name)
    app_link.allow_tags = True
    app_link.short_description = _("app")

custom_site.register(SearchKeyword, SearchKeywordAdmin)
custom_site.register(KeywordLocation, KeywordLocationAdmin)