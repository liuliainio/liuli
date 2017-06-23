from django.utils.translation import ugettext_lazy as _

from estorecore.admin.sites import custom_site
from estorecore.admin import EntityModelAdmin
from estorecore.models.constants import STATS_TAGS
from estoreoperation.statistics.models import CategoryStatistics, ApplicationStatistics, AppVersionStatistics, \
            CategoryFoucsImageStatistics, CategorySubjectStatistics, CategoryRecommendAppStatistics, PreparedAppStatistics, \
            BootAppStatistics, TopAppStatistics


class StatsAdmin(EntityModelAdmin):
    list_per_page = 50

    def __init__(self, model, admin_site):
        super(StatsAdmin, self).__init__(model, admin_site)
        self.tmp_inline_instances = self.inline_instances

    def add_view(self, request, form_url='', extra_context=None):
        self.in_add_view = True
        self.inline_instances = ()    # disable inline edit in add view
        result = super(EntityModelAdmin, self).add_view(request, form_url, extra_context)
        self.inline_instances = self.tmp_inline_instances
        self.in_add_view = False
        return result

    def has_add_permission(self, request):
        return True

    def has_sync_to_permission(self, request, obj=None):
        return True

    def get_actions(self, request):
        actions = super(StatsAdmin, self).get_actions(request)
        if 'delete_selected_items' in actions:
            del actions['delete_selected_items']
        return actions


class CategoryStatsAdmin(StatsAdmin):
    list_display = ('category', 'date', 'clicks', 'tag')
    raw_id_fields = ('category',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-clicks',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('category', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('clicks',),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class ApplicationStatsAdmin(StatsAdmin):
    list_display = ('app', 'date', 'rate', 'ratings', 'clicks', 'downloads', 'tag')
    raw_id_fields = ('app',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-downloads',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('app', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('rate', 'ratings', 'clicks', 'downloads'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class AppVersionStatsAdmin(StatsAdmin):
    list_display = ('appversion', 'date', 'rate', 'ratings', 'clicks', 'downloads', 'tag')
    raw_id_fields = ('appversion',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-downloads',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('appversion', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('rate', 'ratings', 'clicks', 'downloads'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class CategoryFoucsImageStatsAdmin(StatsAdmin):
    list_display = ('categoryfoucsimage', 'date', 'clicks', 'tag')
    raw_id_fields = ('categoryfoucsimage',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-clicks',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('categoryfoucsimage', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('clicks',),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class CategorySubjectStatsAdmin(StatsAdmin):
    list_display = ('categorysubject', 'date', 'clicks', 'tag')
    raw_id_fields = ('categorysubject',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-clicks',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('categorysubject', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('clicks',),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class CategoryRecommendAppStatsAdmin(StatsAdmin):
    list_display = ('categoryrecommend', 'date', 'clicks', 'downloads', 'tag')
    raw_id_fields = ('categoryrecommend',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-downloads',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('categoryrecommend', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('clicks', 'downloads'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class PreparedAppStatsAdmin(StatsAdmin):
    list_display = ('preparedapp', 'date', 'clicks', 'downloads', 'tag')
    raw_id_fields = ('preparedapp',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-downloads',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('preparedapp', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('clicks', 'downloads'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class BootAppStatsAdmin(StatsAdmin):
    list_display = ('bootapp', 'date', 'clicks', 'downloads', 'tag')
    raw_id_fields = ('bootapp',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-downloads',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('bootapp', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('clicks', 'downloads'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class TopAppStatsAdmin(StatsAdmin):
    list_display = ('topapp', 'date', 'clicks', 'downloads', 'tag')
    raw_id_fields = ('topapp',)
    list_filter = ['tag', 'sync_status']
    ordering = ('-downloads',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('topapp', 'date'),
                }),
            (_('Statistics'), {
                'fields': ('clicks', 'downloads'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


custom_site.register(CategoryStatistics, CategoryStatsAdmin)
custom_site.register(ApplicationStatistics, ApplicationStatsAdmin)
custom_site.register(AppVersionStatistics, AppVersionStatsAdmin)
custom_site.register(CategoryFoucsImageStatistics, CategoryFoucsImageStatsAdmin)
custom_site.register(CategorySubjectStatistics, CategorySubjectStatsAdmin)
custom_site.register(CategoryRecommendAppStatistics, CategoryRecommendAppStatsAdmin)
custom_site.register(PreparedAppStatistics, PreparedAppStatsAdmin)
custom_site.register(BootAppStatistics, BootAppStatsAdmin)
custom_site.register(TopAppStatistics, TopAppStatsAdmin)
