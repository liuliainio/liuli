from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.options import csrf_protect_m
from estorecore.models.constants import APP_SOURCES, REVIEW_STATUS, SYNC_STATUS
from estorecore.admin.sites import custom_site
from estorecore.admin import EntityModelAdmin, StackedInline
from estorecore.datasync.sync_app import sync_single_app
from estorecore.admin.filters import SubCategoryFilterSpec
from estoreoperation.app.models import AppVersion
from estoreoperation.admin.newapps.models import ManuallyAddedApp, AutoCrawledApp, DevUploadedApp, AutoMaskOffApp
from estoreoperation.app.models import Application
from estoreoperation.app.admin import AppVersionInline
from estoreoperation.admin.newapps.forms import NewAppAdminForm

_LIST_PER_PAGE = 50


class NewAppsAdmin(EntityModelAdmin):
    readonly_fields = ('package_name', 'package_sig')
    radio_fields = {'tag': admin.HORIZONTAL}
    search_fields = ['name', 'package_name']
    fieldsets = (
        (_('Basic'), {
            'fields': ('name', 'tag'),
            }),
        (_('Category'), {
            'fields': ('category', 'sub_category'),
            }),
        )
    list_filter = ('category', 'sub_category', 'review_status','published','sync_status')
    list_per_page = _LIST_PER_PAGE
    ordering = ('-order',)

    def has_sync_to_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(NewAppsAdmin, self).get_actions(request)
        if 'delete_selected_items' in actions:
            del actions['delete_selected_items']
        return actions

    def versions_link(self, obj):
        return """<a href="/admin/utilities/appversionlist/?app__exact=%s" id="versions_%s" onclick="return showRelatedObjectLookupPopup(this);">
                    <strong>%s</strong>
                </a>""" % (obj.id, obj.id, obj.versions_count)
    versions_link.allow_tags = True
    versions_link.admin_order_field = 'versions_count'
    versions_link.short_description = _("versions")

    def save_model(self, request, obj, form, change):
        old_obj = None if not obj.pk else Application.objects.get(pk__exact=obj.id)
        super(NewAppsAdmin, self).save_model(request, obj, form, change)

        app = Application.objects.get(pk__exact=obj.id)
        if old_obj and old_obj.review_status != REVIEW_STATUS.APPROVED and app.review_status == REVIEW_STATUS.APPROVED \
                and app.published == 1 and not app.hided and app.sync_status == SYNC_STATUS.NEED_SYNC:
            sync_single_app(app)

    class Media:
        js = ("cateapps/js/cateapps.js",)


class NewAppsVersionInline(StackedInline):
    model = AppVersion
    template = 'admin/newapps/stacked.html'
    max_num = 1
    can_delete = False
    ordering = ('-version_code',)
    fieldsets = (
            (_('Version'), {
                'fields': ('version', 'version_code', 'source', 'developer', 'description'),
                }),
            (_('Package'), {
                'fields': ('icon_url', 'icon_path', 'download_url', 'download_path', 'price'),
                }),
            (_('Status'), {
                'fields': ('pub_date', 'published', 'review_status'),
                }),
            )


class ManuallyAddedVersionInline(NewAppsVersionInline):
    fieldsets = (
            (_('Version'), {
                'fields': ('developer', 'description'),
                }),
            (_('Package'), {
                'fields': ('download_path', 'price'),
                }),
            (_('Status'), {
                'fields': ('pub_date', 'published'),
                }),
            )
    change_view_fieldsets = (
            (_('Version'), {
                'fields': ('developer', 'description'),
                }),
            (_('Package'), {
                'fields': ('download_path', 'price'),
                }),
            (_('Status'), {
                'fields': ('pub_date', 'published'),
                }),
            (_('ReadOnly'), {
                'fields': ('icon_path', 'version', 'version_code', 'size')
                }),
            )

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.change_view_fieldsets
        return super(NewAppsVersionInline, self).get_fieldsets(request, obj=obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.change_view_fieldsets[3][1]['fields']
        return ()

    def queryset(self, request):
        qs = super(ManuallyAddedVersionInline, self).queryset(request)
        return qs.filter(source__exact=APP_SOURCES.MANUAL).order_by('-version_code')


class ManuallyAddedAppAdmin(NewAppsAdmin):
    form = NewAppAdminForm
    list_editable = ('published',)
    list_display = ('name', 'full_category', 'versions_link', 'price', \
            'source_name', 'has_icon', 'clicks_count', 'downloads_count', 'rate', 'reviews_count', \
            'modified_time', 'published', 'sync_status')
    list_filter = ('category', 'sub_category','published')
    ordering = ('-order',)

    def change_view(self, request, obj_id):
        self.inlines=[AppVersionInline]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        return super(ManuallyAddedAppAdmin, self).change_view(request, obj_id)

    def add_view(self, request):
        self.inlines=[ManuallyAddedVersionInline]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        return super(ManuallyAddedAppAdmin, self).add_view(request)

    def save_model(self, request, obj, form, change):
        obj.review_status = REVIEW_STATUS.APPROVED
        super(ManuallyAddedAppAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.review_status = REVIEW_STATUS.APPROVED
            instance.source = APP_SOURCES.MANUAL
        super(ManuallyAddedAppAdmin, self).save_formset(request, form, formset, change)


class AutoCrawledVersionInline(NewAppsVersionInline):

    def queryset(self, request):
        qs = super(AutoCrawledVersionInline, self).queryset(request)
        return qs.filter(source__gte=APP_SOURCES.CRAWLED).order_by('-version_code')


class AutoCrawledAppAdmin(NewAppsAdmin):
    list_editable = ('published', 'review_status')
    list_display = ('name', 'app_is_copycat', 'id', 'full_category', 'versions_link', 'source_name', 'published', 'review_status', 'sync_status', \
                    'clicks_count', 'downloads_count', 'rate', 'reviews_count', 'has_icon', 'modified_time')
    ordering = ('-order',)

    def app_is_copycat(self,obj):
        if obj.is_copycat:
            return '<img src="/static/admin/img/admin/icon-no.gif" alt="True">'
        else:
            return '<img src="/static/admin/img/admin/icon-yes.gif" alt="False">'
    app_is_copycat.short_description = _("copycat")
    app_is_copycat.allow_tags = True

    def has_add_permission(self, request, obj=None):
        return False

    def change_view(self, request, obj_id):
        self.inlines=[AppVersionInline]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        return super(AutoCrawledAppAdmin, self).change_view(request, obj_id)

    def add_view(self, request):
        self.inlines=[AutoCrawledVersionInline]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        return super(AutoCrawledAppAdmin, self).add_view(request)

    @csrf_protect_m
    def review_all_apps(self, request):
        reviewed_apps = Application.objects.filter(source__gt=2).filter(review_status__exact=0)
        current_version_ids = [app.current_version.id for app in reviewed_apps if app.current_version]
        reviewed_apps.update(published=1, review_status=1, sync_status=0)
        reviewed_app_versions = AppVersion.objects.filter(pk__in=current_version_ids)
        reviewed_app_versions.update(published=1, review_status=1, sync_status=1)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

'''
    #this function has been canceled and lts change_list btn alos been hiden
    def get_urls(self):
        urlpatterns = super(AutoCrawledAppAdmin, self).get_urls()
        from django.conf.urls.defaults import url
        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns += (
                url(r'^reviewapps$', self.review_all_apps, name='%s_%s_review_all_apps' % info),
            )
        return urlpatterns
'''

class DevUploadedVersionInline(NewAppsVersionInline):
    def queryset(self, request):
        qs = super(DevUploadedVersionInline, self).queryset(request)
        return qs.filter(source__exact=APP_SOURCES.DEV_UPLOAD).order_by('-version_code')


class DevUploadedAppAdmin(NewAppsAdmin):
    form = NewAppAdminForm
    list_editable = ('published', 'review_status')
    list_display = ('name', 'full_category', 'versions_link', \
            'source_name', 'has_icon', 'clicks_count', 'downloads_count', 'rate', 'reviews_count', \
            'modified_time', 'published', 'review_status', 'sync_status')

    def change_view(self, request, obj_id):
        self.inlines=[AppVersionInline]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        return super(DevUploadedAppAdmin, self).change_view(request, obj_id)

    def add_view(self, request):
        self.inlines=[DevUploadedVersionInline]
        self.inline_instances = []
        for inline_class in self.inlines:
            inline_instance = inline_class(self.model, self.admin_site)
            self.inline_instances.append(inline_instance)
        return super(DevUploadedAppAdmin, self).add_view(request)

    def has_add_permission(self, request, obj=None):
        return False


class AutoMaskOffAppAdmin(EntityModelAdmin):
    list_editable = ('order', 'published', 'review_status')
    list_display = ('order', 'package_name', 'reason', 'modified_time', 'published', 'review_status','sync_status')
    ordering = ('order',)
    list_display_links = ('package_name',)
    search_fields = ['package_name']
    fieldsets = (
            (_('Basic'), {
                'fields': ('package_name', 'reason'),
                }),
            (_('Status'), {
                'fields': ('review_status', 'published'),
                }),
            )


custom_site.register(ManuallyAddedApp, ManuallyAddedAppAdmin)
custom_site.register(AutoCrawledApp, AutoCrawledAppAdmin)
custom_site.register(DevUploadedApp, DevUploadedAppAdmin)
custom_site.register(AutoMaskOffApp, AutoMaskOffAppAdmin)
