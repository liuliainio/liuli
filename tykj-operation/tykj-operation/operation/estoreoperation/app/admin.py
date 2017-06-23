#! -*- coding: utf-8 -*-
import datetime
from django.db.models import F
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from ajax_select import make_ajax_form
from estorecore.admin.sites import custom_site
from estorecore.datasync.sync_app import sync_obj
from django.http import HttpResponseRedirect
from estorecore.models.constants import REVIEW_STATUS, BELONGTOS, APP_LIST_TYPES, SYNC_STATUS, RICHITEM_TYPE
from estorecore.admin import EntityModelAdmin, TabularInline, CommonBaseAdmin
from estoreoperation.app.forms import CategoryAdminForm, AppVersionAdminForm, \
        CategoryFoucsImageAdminForm, PreparedAppAdminForm, BootAppAdminForm, ApplicationAdminForm
from estoreoperation.app.models import AppVersion, PreviewIcon, SubjectApp, KuWanApp, KuWanItem, \
        SubjectItem, Application, CategorySubject, AppList
from django.contrib.contenttypes.models import ContentType
from estorecore.models.app import CheckApp, AppChannelList

_LIST_PER_PAGE = 20


class BaseAppListItemAdmin(EntityModelAdmin, CommonBaseAdmin):

    def save_model(self, request, obj, form, change):
        pre_save_status = self.pre_save_model(request, obj, form, change)
        if not pre_save_status:
            return

        if not obj.pk:    # new
            obj.creator = request.user
            obj.created_time = datetime.datetime.now()
            if hasattr(obj, 'order'):
                obj.order = 1
        obj.modified_time = datetime.datetime.now()
        obj.modifier = request.user
        obj.sync_status = 0
        # check the published and review_status fields
        old_obj = self.model.objects.get(pk=obj.id) if obj.pk else None
        # if published field changed from False to True or this model is created with published is True,
        # check review_status, if not APPROVED, set published False
        if (not old_obj or not old_obj.published) and obj.published:
            status, msg = self._can_published_or_not(obj)
            if not status:
                obj.published = False
                messages.error(request, msg)

        #synced_items = self.queryset(request).filter(sync_status=SYNC_STATUS.SYNCED)
        #has_synced_ids = []
        #for item in synced_items:
        #    has_synced_ids.append(item.id)

        if not old_obj or old_obj.order != obj.order:
            need_adjust_items, adjust_amount = self._get_need_adjust_items(request, old_obj, obj) \
                    if old_obj else (self.queryset(request), 1)
            need_adjust_items.update(order=F('order') + adjust_amount, sync_status=SYNC_STATUS.NEED_SYNC)

            # when create new obj, sync all items whose sync_status is SYNCED
            # before add this new obj.
            #if not old_obj and has_synced_ids:
            #    for item in self.queryset(request).filter(pk__in=has_synced_ids):
            #        sync_obj(item, self.model)
        obj.save()
        #for auto off-shelve app
        if obj.published and obj.review_status == 1:
            fkp = obj.app if getattr(obj,'app',None) else None
            if not fkp and obj.type and obj.type in (RICHITEM_TYPE.APP_DETAILES_PAGE,):
                pid = obj.attr
                apps = Application.objects.filter(pk__exact=pid)
                fkp = apps[0] if apps else None

            if fkp and not CheckApp.objects.filter(obj_id=obj.id,app=fkp,hided=0):
                capp = CheckApp()
                capp.content_type = ContentType.objects.get_for_model(obj)
                capp.obj_id = obj.id
                capp.app = fkp
                capp.model_name = self.__class__.__name__.lower() + u'|' + self.opts.verbose_name
                capp.save()


class CategoryAdmin(EntityModelAdmin):
    form = CategoryAdminForm
    list_editable = ('order', 'published', 'review_status')
    list_display = ('order', 'name', 'description', 'icon_path', 'level', 'parent_category', \
            'click_count', 'modified_time', 'published', 'review_status', 'sync_status')
    list_display_links = ('name',)
    list_per_page = _LIST_PER_PAGE
    list_filter = ['level', 'sync_status', 'review_status','published']
    search_fields = ['name', 'description']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('name', 'description', 'icon_path', 'level', 'parent_category'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(CategoryAdmin, self).get_actions(request)
        if 'delete_selected_items' in actions:
            del actions['delete_selected_items']
        return actions


class PreviewIconInline(TabularInline):
    template = 'admin/app/preview_tabular.html'
    model = PreviewIcon
    fields = ('order', 'title', 'path', 'url')

    def queryset(self, request):
        qs = super(PreviewIconInline, self).queryset(request)
        return qs.filter(hided__exact=False)


class AppVersionAdmin(EntityModelAdmin):
    form = AppVersionAdminForm
    readonly_fields = ('version_code', 'package_hash')
    list_editable = ('published',)
    list_display = ('app_version', 'source_name', 'price', 'size', 'pub_date', 'version_code', 'click_count', \
            'download_count', 'rate', 'published')
    list_per_page = _LIST_PER_PAGE
    search_fields = ['app__name', 'app__package_name', 'developer', 'description', 'version']
    ordering = ('-created_time',)
    raw_id_fields = ('app',)
    inlines = (PreviewIconInline,)
    fieldsets = (
            (_('Basic'), {
                'fields': ('app', 'source', 'developer', 'description', 'update_note', 'price', 'pub_date', 'icon_url', 'icon_path', 'download_path', 'package_hash', 'version', 'size', 'reviewed_desc_preview'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            (_('Tianyi Status'), {
                'fields': ('t_status',),
                }),
            )

    def has_sync_to_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_actions(self, request):
        actions = super(AppVersionAdmin, self).get_actions(request)
        if 'delete_selected_items' in actions:
            del actions['delete_selected_items']
        return actions

    #def get_fieldsets(self, request, obj=None):
    #    if obj:
    #        if request.user.is_superuser or request.user.has_perm('auth.view_tianyi_status'):
    #            return self.basic_fieldsets + ((_('Tianyi Status'), {'fields': ('t_status',),}),)
    #        else:
    #            return self.basic_fieldsets
    #    return super(EntityModelAdmin, self).get_fieldsets(request, obj=obj)

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['pub_date'].initial = datetime.datetime.now()
        context['is_sync_button_show'] = True
        return super(AppVersionAdmin, self).render_change_form(request, context, *args, **kwargs)
        #telecom-cnet app download address support delayed to next iteration
        #app_id = kwargs['obj'].app.id
        #download_link = u'http://estoresrvice.189store.com/api/app/download/app.json?clientid=%s&app_id=%s' % (app_id,app_id)
        #hyper_widget = context['adminform'].form.fields['hyper_download_url'].widget
        #hyper_widget.target_link = hyper_widget.target_name = download_link

    #override parent class for appversion
    def response_change(self, request, obj):
        app = obj.app
        app_category_id = app.category.id
        return_url = '/admin/cateapps/application' + str(app_category_id)

        if "_saveandsync" in request.POST:
            if obj.review_status == REVIEW_STATUS.APPROVED:
                sync_obj(app, Application)
                self.message_user(request, _("The %(name)s \"%(obj)s\" was changed successfully, and successfully synced to production.") %
                    {'name': force_unicode(self.opts.verbose_name), 'obj': force_unicode(app)})
                return HttpResponseRedirect(return_url)
        return super(AppVersionAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):
        super(AppVersionAdmin, self).save_model(request, obj, form, change)
        all_version_codes = [v.version_code for v in obj.app.versions.all()]
        is_max = True
        for v in all_version_codes:
            if v > obj.version_code:
                is_max = False
                break
        if is_max:
            obj.app.current_version = obj
            obj.app.current_version_name = obj.version
            obj.app.sync_status = 0
        obj.app.modified_time = datetime.datetime.now()
        obj.app.modifier = request.user
        obj.app.save()


class AppVersionInline(TabularInline):
    template = 'admin/app/tabular.html'
    model = AppVersion
    fields = ('version', 'version_code', 'source', 'download_path', 'reviewed_desc_preview', 'published', 'review_status')
    readonly_fields = ('version', 'version_code', 'source', 'download_path', 'reviewed_desc_preview')
    extra = 0
    can_delete = False
    ordering = ('-version_code',)


class ApplicationAdmin(EntityModelAdmin):
    radio_fields = {'tag': admin.HORIZONTAL}
    list_display = ('id', 't_id', 't_chargemode', 't_paytype', 'name', 'current_version_name', 'full_category', \
            'has_icon', 'price', 'clicks_count', 'downloads_count', 'rate', 'sync_status', 'view_detail')
    list_per_page = _LIST_PER_PAGE
    search_fields = ['name', 'package_name', 't_id', 'id']
    ordering = ('-order',)
    inlines = (AppVersionInline,)
    list_filter = ('t_paytype',)
    form = make_ajax_form(Application, {
                            'current_version': 'app_version',
                            'prev_version': 'app_version',
                        },
                        superclass=ApplicationAdminForm)
    fieldsets = (
            (_('Basic'), {
                'fields': ('name', 'package_name', 'package_sig', 'tag','blocked_devices'),
                }),
            (_('App Label'), {
                'fields': ('label',),
                }),
            (_('Category'), {
                'fields': ('category', 'sub_category', 't_paytype'),
                }),
            (_('Versions'), {
                'fields': ('current_version', 'prev_version'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status', 'unpublished_reason'),
                }),
            (_('Tianyi Status'), {
                'fields': ('t_id', 't_chargemode', 't_status'),
                }),
            )

    def has_add_permission(self, request):
        return False

    def has_sync_to_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def get_actions(self, request):
        actions = super(ApplicationAdmin, self).get_actions(request)
        if 'delete_selected_items' in actions:
            del actions['delete_selected_items']
        return actions

    #def get_fieldsets(self, request, obj=None):
    #    if not (request.user.is_superuser or request.user.has_perm('auth.view_tianyi_status')):
    #        self.fieldsets[4][1]['fields'] = ('t_id', 't_chargemode')
    #    else:
    #        self.fieldsets[4][1]['fields'] = ('t_id', 't_status', 't_chargemode')
    #    return super(EntityModelAdmin, self).get_fieldsets(request, obj=obj)

    def _can_published_or_not(self, obj):
        if obj.sub_category == None:
            return False, _("Sub category should not be None for object: %(obj)s") % {'obj': obj}
        elif obj.current_version == None:
            return False, _("Current version should not be None for object: %(obj)s") % {'obj': obj}
        elif obj.review_status != REVIEW_STATUS.APPROVED or obj.current_version.review_status != REVIEW_STATUS.APPROVED:
            return False, _("You can't publish not approved %(model)s: %(obj)s") % {'model': self.model._meta.verbose_name, 'obj': obj}
        return True, ''

    def versions_link(self, obj):
        return """<a href="/admin/utilities/appversionlist/?app__exact=%s" id="versions_%s" onclick="return showRelatedObjectLookupPopup(this);">
                    <strong>%s</strong>
                </a>""" % (obj.id, obj.id, obj.versions_count)
    versions_link.allow_tags = True
    versions_link.admin_order_field = 'versions_count'
    versions_link.short_description = _("versions")

    def view_detail(self, obj):
        return """<a href="/admin/app/application/%s/" onclick="return showRelatedObjectLookupPopup(this);">
                    <strong>%s</strong>
                </a>""" % (obj.id, _("view detail").encode('utf-8'))
    view_detail.allow_tags = True
    view_detail.short_description = _("view detail")


class CategoryFoucsImageAdmin(BaseAppListItemAdmin):
    form = CategoryFoucsImageAdminForm
    list_editable = ('order', 'published', 'review_status')
    list_display = ('order', 'id', 'type', 'attr_readable', 'click_count', 'modified_time', 'published', 'review_status', 'sync_status')
    list_display_links = ('id',)
    list_filter = ['type', 'sync_status', 'review_status','published']
    list_per_page = _LIST_PER_PAGE
    search_fields = ['type', 'attr']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('pub_date', 'icon_path'),
                }),
            (_('Type'), {
                'fields': ('type', 'attr', 'cooperate_list_id', 'cooperate_list_name'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['pub_date'].initial = datetime.datetime.now()
        return super(CategoryFoucsImageAdmin, self).render_change_form(request, context, *args, **kwargs)


class CategorySubjectAdmin(EntityModelAdmin):
    list_editable = ('order', 'published', 'clicks_count')
    list_display = ('order', 'name', 'id', 'sub_title', 'description', 'pub_date', 'icon_path', \
            'clicks_count', 'modified_time', 'published', 'review_status', 'sync_status')
    list_display_links = ('name',)
    list_per_page = _LIST_PER_PAGE
    search_fields = ['name', 'sub_title', 'description']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('name', 'sub_title', 'description', 'subject_tml', 'pub_date', 'icon_path', 'large_icon_path', 'large_icon_url'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )


class CategoryRecommendAppAdmin(BaseAppListItemAdmin):
    list_editable = ('order', 'published', 'review_status')
    list_display = ('app', 'version', 'type', 'pub_date', 'source', 'has_icon', \
            'versions_count', 'reviews_count', 'click_count', 'download_count', 'rate', \
            'modified_time', 'order', 'published', 'review_status', 'sync_status')
    list_per_page = _LIST_PER_PAGE
    search_fields = ['app__name']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('app', 'pub_date'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
        )
    raw_id_fields = ('app',)

    def __init__(self, model, admin_site):
        super(CategoryRecommendAppAdmin, self).__init__(model, admin_site)
        self.tmp_inline_instances = self.inline_instances

    def add_view(self, request, form_url='', extra_context=None):
        self.in_add_view = True
        self.inline_instances = ()    # disable inline edit in add view
        result = super(EntityModelAdmin, self).add_view(request, form_url, extra_context)
        self.inline_instances = self.tmp_inline_instances
        self.in_add_view = False
        return result

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['pub_date'].initial = datetime.datetime.now()
        return super(CategoryRecommendAppAdmin, self).render_change_form(request, context, *args, **kwargs)

    def versions_link(self, obj):
        return """<a href="/admin/utilities/appversionlist/?app__exact=%s" id="versions_%s" onclick="return showRelatedObjectLookupPopup(this);">
                    <strong>%s</strong>
                </a>""" % (obj.id, obj.id, obj.versions_count())
    versions_link.allow_tags = True
    versions_link.short_description = _("versions")


class PreparedAppAdmin(BaseAppListItemAdmin):
    form = PreparedAppAdminForm
    list_editable = ('order', 'published', 'review_status')
    list_display = ('app', 'version', 'full_category', 'source', 'has_icon', 'versions_count', \
            'reviews_count', 'click_count', 'download_count', 'rate', 'modified_time', \
            'order', 'published', 'review_status', 'sync_status')
    list_per_page = _LIST_PER_PAGE
    search_fields = ['app__name']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('app',),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )
    raw_id_fields = ('app',)


class BootAppAdmin(BaseAppListItemAdmin):
    form = BootAppAdminForm
    list_editable = ('order', 'published', 'review_status')
    list_display = ('app', 'version', 'full_category', 'source', 'has_icon', 'versions_count', \
            'reviews_count', 'click_count', 'download_count', 'rate', 'modified_time', \
            'order', 'published', 'review_status', 'sync_status')
    list_per_page = _LIST_PER_PAGE
    search_fields = ['app__name']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('app', 'boot_app_type'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )
    raw_id_fields = ('app',)


class TopAppAdmin(BaseAppListItemAdmin):
    list_editable = ('order', 'published', 'review_status')
    list_display = ('app', 'version', 'full_category', 'source', 'has_icon', 'versions_count', \
            'reviews_count', 'click_count', 'download_count', 'rate', 'modified_time', \
            'order', 'published', 'review_status', 'sync_status')
    list_per_page = _LIST_PER_PAGE
    search_fields = ['app__name']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('app','short_desc'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )
    raw_id_fields = ('app',)


class SubjectAppRelationshipInline(admin.TabularInline):
    extra = 1
    model = SubjectApp
    raw_id_fields = ('app',)


class SubjectItemAdmin(EntityModelAdmin):
    list_editable = ('order', 'published')
    list_display = ('order', 'title', 'subject', 'description', 'icon_path', 'modified_time', \
            'published', 'review_status', 'sync_status')
    list_display_links = ('title',)
    list_per_page = _LIST_PER_PAGE
    search_fields = ['title', 'subject__name', 'description']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('subject', 'title', 'description', 'icon_url', 'icon_path'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )
    raw_id_fields = ('subject',)
    inlines = (SubjectAppRelationshipInline,)


class KuWanAppRelationshipInline(admin.TabularInline):
    extra = 1
    model = KuWanApp
    raw_id_fields = ('app',)


class KuWanItemAdmin(EntityModelAdmin):
    list_editable = ('order', 'published')
    list_display = ('order', 'title', 'description', 'price', 'icon_path', 'modified_time', \
            'published', 'review_status', 'sync_status')
    list_display_links = ('title',)
    list_per_page = _LIST_PER_PAGE
    search_fields = ['title', 'description']
    ordering = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('title', 'description', 'price', 'list_type', 't_id', 'icon_url', 'icon_path'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )
    inlines = (KuWanAppRelationshipInline,)


class AppReviewAdmin(EntityModelAdmin):
    list_editable = ('rate', 'published')
    list_display = ('review_id', 'user_id', 'user_name', 'app_version_name', 'comment', 'rate', 'created_time', 'published', 'sync_status')
    list_per_page = _LIST_PER_PAGE
    list_filter = ['sync_status', 'tag', 'hided','published']
    search_fields = ['app_version__app__name', 'comment', 'user_name']
    ordering = ('-created_time',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('user_id', 'user_name', 'app_version', 'rate', 'comment', 'created_time'),
                }),
            (_('Status'), {
                'fields': ('review_status', 'published'),
                }),
            )
    raw_id_fields = ('app_version',)
    special_exclude = ('sync_status',)
    special_readonly = ('sync_status',)

    def save_model(self, request, obj, form, change):
        obj.sync_status = 0
        obj.review_status = 1
        obj.save()

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        if request.method == "POST":
            objs = formset.save(commit=False)
            for obj in objs:
                obj.sync_status = 0
                obj.save()
            formset.save_m2m()

    def has_delete_permission(self, request, obj=None):
        return True


class AppListAdmin(EntityModelAdmin):
    readonly_fields = ('belong_to',)
    list_editable = ('published', 'review_status')
    list_display = ('name', 'codename', 'list_type', 'published', 'review_status', 'sync_status')
    list_per_page = _LIST_PER_PAGE
    list_filter = ('sync_status', 'list_type','published')
    search_fields = ['name']
    ordering = ('-created_time',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('name', 'codename', 'list_type'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )

    def save_model(self, request, obj, form, change):
        obj.belong_to = BELONGTOS.CTAPPSTORE
        super(AppListAdmin, self).save_model(request, obj, form, change)


class AppChannelListAdmin(ApplicationAdmin):
    list_display = ('id', 'name', 't_id', 't_chargemode', 't_paytype', 'current_version_name', 'version_status', 'full_category',
                    'price', 'clicks_count', 'downloads_count', 'sync_status', 'has_icon')
    list_display_links = ('id', 'name')
    list_filter = ['t_paytype', 'sync_status', 'review_status', 'published']

    def version_status(self, obj):
        max_version = obj.versions.all().order_by('-version_code')[0].version_code
        cur_version = obj.current_version.version_code
        show_img = '<img src="/static/admin/img/admin/icon-yes.gif" alt="True">'
        if max_version > cur_version:
            show_img = '<img src="/static/admin/img/admin/icon-no.gif" alt="False">'
        return show_img
    version_status.allow_tags = True
    version_status.short_description = _("is new version")

    def render_change_form(self, request, context, *args, **kwargs):
        context['is_sync_button_show'] = True
        return super(AppChannelListAdmin, self).render_change_form(request, context, *args, **kwargs)

    def has_sync_to_permission(self, request, obj=None):
        return True


custom_site.register(Application, ApplicationAdmin)
custom_site.register(AppVersion, AppVersionAdmin)
custom_site.register(CategorySubject, CategorySubjectAdmin)
custom_site.register(SubjectItem, SubjectItemAdmin)
custom_site.register(AppList, AppListAdmin)
custom_site.register(AppChannelList, AppChannelListAdmin)
