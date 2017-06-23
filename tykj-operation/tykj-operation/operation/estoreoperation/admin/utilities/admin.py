from django.http import HttpResponse

from estorecore.admin.sites import custom_site
from estoreoperation.admin.utilities.models import SearchApp, AppVersionList, PopAppVersion, SubjectApplication
from estoreoperation.app.admin import ApplicationAdmin, AppVersionAdmin, SubjectItemAdmin


class SearchAppAdmin(ApplicationAdmin):
    list_editable = ()
    list_display = ('name', 'current_version_name', 'full_category', 'versions_link', 'price', \
            'source', 'has_icon', 'published', 'review_status')
    list_filter = []

    def has_add_permission(self, request):
        return False

    def has_sync_to_permission(self, request, obj=None):
        return False

    class Media:
        js = ("cateapps/js/cateapps.js",)


class AppVersionListAdmin(AppVersionAdmin):
    list_display = ('app_version', 'source', 'price', 'size', 'pub_date', 'click_count', \
            'download_count', 'rate',  'published')

    def has_add_permission(self, request):
        return False

    def has_sync_to_permission(self, request, obj=None):
        return False


class PopAppVersionAdmin(AppVersionAdmin):
    def response_change(self, request, obj):
        if '_popup' in request.POST:
            return HttpResponse('<script type="text/javascript">opener.dismissRelatedLookupPopup(window);</script>')
        return super(PopAppVersionAdmin, self).response_change(request, obj)


class SubjectApplicationAdmin(SubjectItemAdmin):
    list_display = ('order', 'title', 'subject', 'description', 'icon_path', 'modified_time', 'modifier_name', \
            'published', 'review_status', 'sync_status')

    def response_change(self, request, obj):
        if '_popup' in request.REQUEST:
            return HttpResponse('<script type="text/javascript">opener.dismissRelatedLookupPopup(window);</script>')
        return super(SubjectApplicationAdmin, self).response_change(request, obj)

    class Media:
        js = ("subject/js/subject.js",)


custom_site.register(SearchApp, SearchAppAdmin)
custom_site.register(AppVersionList, AppVersionListAdmin)
custom_site.register(PopAppVersion, PopAppVersionAdmin)
custom_site.register(SubjectApplication, SubjectApplicationAdmin)
