from estorecore.admin.sites import custom_site
from estorecore.admin.filters import SubCategoryFilterSpec
from estoreoperation.app.admin import ApplicationAdmin
from estoreoperation.admin.updateapps.models import AppUpdateNoScreenshots, AppUpdateWithScreenshots


class AppUpdateNoScreenshotsAdmin(ApplicationAdmin):
    list_editable = ('published',)
    list_display = ('name', 'current_version', 'prev_version', 'full_category', 'versions_link', \
            'source_name', 'has_icon', 'clicks_count', 'downloads_count', 'rate', 'reviews_count', \
            'modified_time', 'published', 'sync_status')
    list_filter = ('category', 'sub_category','published')

    def has_add_permission(self, request, obj=None):
        return False

    class Media:
        js = ("cateapps/js/cateapps.js",)


class AppUpdateWithScreenshotsAdmin(ApplicationAdmin):
    list_editable = ('published', 'review_status')
    list_display = ('name', 'current_version', 'prev_version', 'full_category', 'versions_link', \
            'source_name', 'has_icon', 'reviews_count', 'clicks_count', 'downloads_count', 'rate', \
            'modified_time', 'published', 'review_status', 'sync_status')
    list_filter = ('category', 'sub_category', 'review_status','published')

    def has_add_permission(self, request, obj=None):
        return False

    class Media:
        js = ("cateapps/js/cateapps.js",)


custom_site.register(AppUpdateNoScreenshots, AppUpdateNoScreenshotsAdmin)
custom_site.register(AppUpdateWithScreenshots, AppUpdateWithScreenshotsAdmin)
