import datetime
from django import forms
from django.db.models import F
from django.utils import simplejson
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from estorecore.admin import EntityModelAdmin, CommonBaseAdmin
from estorecore.admin.sites import custom_site
from estorecore.datasync.sync_app import sync_obj
from estorecore.models.constants import SYNC_STATUS, APP_LIST_TYPES, GAME_APP_DISPLAY_MODE, RICHITEM_TYPE
from estoreoperation.admin.cateapps.models import get_category
from estoreoperation.app.admin import CategoryRecommendAppAdmin, PreparedAppAdmin, BootAppAdmin, \
        TopAppAdmin, KuWanItemAdmin
from estoreoperation.admin.applist.models import applistitem_factory, \
        AppList, BELONGTOS, RECOMMEND_TYPES, NewestRecommendApp, HottestRecommendApp, \
        MatchestRecommendApp, HomeNewRecommendApp, PreparedApp, BootApp, \
        ApplicationTopApp, GameTopApp, ReadingTopApp, MusicVideoTopApp, TianYiKuWanItem
from estoreoperation.admin.applist.forms import AppListItemAdminForm, BannerAppListItemAdminForm, \
        NewestRecommendAppForm, HottestRecommendAppForm, MatchestRecommendAppForm, HomeNewRecommendAppForm, \
        ApplicationTopAppForm, GameTopAppForm, ReadingTopAppForm, MusicVideoTopAppForm, KuWanItemAdminForm, \
        WebAppBannerListAdminForm, OrderAreaBannerListAdminForm, GameAppListAdminForm
from django.contrib.contenttypes.models import ContentType
from estorecore.models.app import CheckApp,Application

_LIST_PER_PAGE = 20


class AppListItemAdmin(EntityModelAdmin, CommonBaseAdmin):
    form = AppListItemAdminForm
    list_per_page = _LIST_PER_PAGE
    list_editable = ('order', 'published', 'review_status')
    list_display = ('order', 'app_id', 'app_link', 'modified_time', \
            'published', 'review_status', 'sync_status', 'app_status')
    list_display_links = ('app_id',)
    list_filter = ('sync_status', 'app__category','published')
    search_fields = ['app__name', 'app__package_name']
    ordering = ('order',)
    readonly_fields = ('order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('app', 'app_list', 'icon_url', 'icon_path'),
                }),
            (_('Extra Infos'), {
                'fields': ('extra_kuwan_price', 'extra_editor_category', 'extra_added_price', 'extra_added_desc'),
                'classes': ('collapse',)
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
        )

    raw_id_fields = ('app',)
    custom_group = True

    def app_status(self,obj):
        is_published = obj.app.published
        if is_published == 0:
            txt = _("off shelve")
        else:
            txt = _("Ok")
        return txt
    app_status.allow_tags = True
    app_status.short_description = _("app status")

    def __init__(self, model, admin_site):
        super(AppListItemAdmin, self).__init__(model, admin_site)
        self.tmp_inline_instances = self.inline_instances

    def add_view(self, request, form_url='', extra_context=None):
        self.in_add_view = True
        self.inline_instances = ()    # disable inline edit in add view
        result = super(EntityModelAdmin, self).add_view(request, form_url, extra_context)
        self.inline_instances = self.tmp_inline_instances
        self.in_add_view = False
        return result

    def app_link(self, obj):
        info = self.model._meta.app_label, self.model._meta.module_name
        return """<a href="/admin/app/application/%s/?rtn_url=%s" target="_blank"><strong>%s</strong></a>""" \
                % (obj.app.id, reverse('admin:%s_%s_changelist' % info), obj.app.name)
    app_link.allow_tags = True
    app_link.short_description = _("app")

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['app_list'].initial = self.app_list
        return super(AppListItemAdmin, self).render_change_form(request, context, *args, **kwargs)

    def queryset(self, request):
        filtered_queryset = super(AppListItemAdmin, self).queryset(request).filter(app_list=self.app_list)
        return self.post_queryset(request, filtered_queryset)

    def has_sync_to_permission(self, request, obj=None):
        return True

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
        if obj.published and obj.review_status == 1 and \
               obj.app_list.codename != u'whitelist' and \
               not CheckApp.objects.filter(obj_id=obj.id,app=obj.app,hided=0):
            fkp = obj.app if obj.app else None
            if not fkp and obj.type and obj.type in (RICHITEM_TYPE.APP_DETAILES_PAGE,):
                pid = obj.attr
                apps = Application.objects.filter(pk__exact=pid)
                fkp = apps[0] if apps else None

            if fkp:
                capp = CheckApp()
                capp.content_type = ContentType.objects.get_for_model(obj)
                capp.obj_id = obj.id
                capp.app = fkp
                capp.model_name = self.__class__.__name__.lower() + u'|' + self.opts.verbose_name
                capp.save()

    class Media:
        js = ("applist/js/applist.js",)


class BannerAppListItemAdmin(AppListItemAdmin):
    form = BannerAppListItemAdminForm
    list_display = ('order', 'id', 'title', 'type', 'attr_readable',  'modified_time', \
            'published', 'review_status', 'sync_status')
    list_display_links = ('id',)
    list_filter = ('sync_status', 'type','published')
    search_fields = ['title']
    fieldsets = (
            (_('Basic'), {
                'fields': ('app_list',),
                }),
            (_('Rich'), {
                'fields': ('type', 'attr', 'title', 'description', 'icon_url', 'icon_path'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
        )


class GameAppListAdmin(AppListItemAdmin):
    form = GameAppListAdminForm
    list_display = ('order', 'app_id', 'app_link', 'display_mode', 'modified_time', \
            'published', 'review_status', 'sync_status')
    fieldsets = (
            (_('Basic'), {
                'fields': ('app', 'app_list', 'extra_display_mode', 'icon_url', 'icon_path'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
        )

    def display_mode(self, obj):
        if obj.extra_infos:
            extra_infos = simplejson.loads(obj.extra_infos)
            if 'display_mode' in extra_infos:
                return GAME_APP_DISPLAY_MODE.to_dict().get(int(extra_infos['display_mode']), '')
        return ''
    display_mode.short_description = _('display mode')

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['icon_path'].help_text = _('Please upload JPEG, PNG, GIF files, size: top area big banner: 480x220, double column small banner: 237x95, single column middle banner: 480x115, double column game app: 237x115.')
        return super(GameAppListAdmin, self).render_change_form(request, context, *args, **kwargs)


class WebAppBannerListAdmin(BannerAppListItemAdmin):
    form = WebAppBannerListAdminForm
    fieldsets = (
            (_('Basic'), {
                'fields': ('app_list',),
                }),
            (_('Rich'), {
                'fields': ('type', 'attr', 'extra_rate', 'extra_views_count', 'title', 'description', 'icon_url', 'icon_path', 'extra_app_icon_url'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
        )

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['icon_path'].help_text = _('Please upload JPEG, PNG, GIF files, size: 220x130')
        return super(WebAppBannerListAdmin, self).render_change_form(request, context, *args, **kwargs)


class OrderAreaBannerListAdmin(BannerAppListItemAdmin):
    form = OrderAreaBannerListAdminForm
    fieldsets = (
            (_('Basic'), {
                'fields': ('app_list',),
                }),
            (_('Rich'), {
                'fields': ('type', 'attr', 'title', 'description', 'icon_url', 'icon_path'),
                }),
            (_('Extra infos'), {
                'fields': ('extra_order_id', 'extra_order_url', 'extra_price', 'extra_title'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
        )

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['icon_path'].help_text = _('Please upload JPEG, PNG, GIF files, size: 480x375')
        return super(OrderAreaBannerListAdmin, self).render_change_form(request, context, *args, **kwargs)


def applistitemadmin_factory(class_s, app_list, model=AppListItemAdmin):

    class_attrs = {
        'app_list': app_list,
        '__module__': __name__,
    }
    class_name = '%s%s' % (model.__name__, class_s)
    return forms.MediaDefiningClass(class_name, (model,), class_attrs)

BANNER_ADMIN_MAPPING = {
    'webapps': WebAppBannerListAdmin,
    'order_area': OrderAreaBannerListAdmin,
}

for app_list in AppList.objects.all():
    model = applistitem_factory('%sA%s' % (BELONGTOS.get_key(app_list.belong_to), app_list.id), app_list)
    if app_list.list_type == APP_LIST_TYPES.DEFAULT:
        admin_model = applistitemadmin_factory('%sA%s' % (BELONGTOS.get_key(app_list.belong_to), app_list.id), app_list)
    elif app_list.list_type == APP_LIST_TYPES.GAME_LIST:
        admin_model = applistitemadmin_factory('%sA%s' % (BELONGTOS.get_key(app_list.belong_to), app_list.id), \
                app_list, model=GameAppListAdmin)
    else:
        admin_model = applistitemadmin_factory('%sA%s' % (BELONGTOS.get_key(app_list.belong_to), app_list.id), \
                app_list, model=BANNER_ADMIN_MAPPING.get(app_list.codename, BannerAppListItemAdmin))
    custom_site.register(model, admin_model)


class RecommendedAppAdmin(CategoryRecommendAppAdmin):
    list_editable = ('order', 'published', 'review_status')
    list_display = ('order', 'app_id', 'app_link', 'version', 'rate', 'click_count', \
            'download_count', 'reviews_count', 'modified_time', 'source', \
            'has_icon', 'published', 'review_status', 'sync_status', 'app_status')
    list_display_links = ('app_id',)
    list_filter = ('sync_status', 'review_status','published')

    def app_status(self,obj):
        is_published = obj.app.published
        if is_published == 0:
            txt = _("off shelve")
        else:
            txt = _("Ok")
        return txt
    app_status.allow_tags = True
    app_status.short_description = _("app status")

    def app_link(self, obj):
        info = self.model._meta.app_label, self.model._meta.module_name
        return """<a href="/admin/app/application/%s/?rtn_url=%s" target="_blank"><strong>%s</strong></a>""" \
                % (obj.app.id, reverse('admin:%s_%s_changelist' % info), obj.app.name)
    app_link.allow_tags = True
    app_link.short_description = _("app")

    def save_model(self, request, obj, form, change):
        obj.type = self.type_
        super(RecommendedAppAdmin, self).save_model(request, obj, form, change)

    def queryset(self, request):
        return super(RecommendedAppAdmin, self).queryset(request).filter(type__exact=self.type_)

    def has_sync_to_permission(self, request, obj=None):
        return True

    class Media:
        js = ("applist/js/applist.js",)


class NewestRecommendedAppAdmin(RecommendedAppAdmin):
    form = NewestRecommendAppForm

    def __init__(self, *args, **kwargs):
        self.type_ = RECOMMEND_TYPES.NEWEST
        super(NewestRecommendedAppAdmin, self).__init__(*args, **kwargs)


class HottestRecommendedAppAdmin(RecommendedAppAdmin):
    form = HottestRecommendAppForm

    def __init__(self, *args, **kwargs):
        self.type_ = RECOMMEND_TYPES.HOTTEST
        super(HottestRecommendedAppAdmin, self).__init__(*args, **kwargs)


class MatchestRecommendedAppAdmin(RecommendedAppAdmin):
    form = MatchestRecommendAppForm
    custom_group = True

    def __init__(self, *args, **kwargs):
        self.type_ = RECOMMEND_TYPES.MATCHEST
        super(MatchestRecommendedAppAdmin, self).__init__(*args, **kwargs)

    def queryset(self, request):
        super_queryset = super(MatchestRecommendedAppAdmin, self).queryset(request)
        return self.post_queryset(request, super_queryset)


class HomeNewRecommendedAppAdmin(RecommendedAppAdmin):
    form = HomeNewRecommendAppForm

    def __init__(self, *args, **kwargs):
        self.type_ = RECOMMEND_TYPES.HOME_NEW
        super(HomeNewRecommendedAppAdmin, self).__init__(*args, **kwargs)


class PreparedAppAdmin(PreparedAppAdmin):
    list_display = ('order', 'app_id', 'app_link', 'version', 'full_category', 'rate', 'click_count', 'download_count', \
            'reviews_count', 'modified_time', 'has_icon', 'published', 'review_status', 'sync_status')
    list_display_links = ('app_id',)
    list_filter = ('sync_status', 'review_status','published')

    def versions_link(self, obj):
        return """<a href="/admin/utilities/appversionlist/?app__exact=%s" id="versions_%s" onclick="return showRelatedObjectLookupPopup(this);">
                    <strong>%s</strong>
                </a>""" % (obj.app.id, obj.id, obj.versions_count())
    versions_link.allow_tags = True
    versions_link.short_description = _("versions")

    def app_link(self, obj):
        info = self.model._meta.app_label, self.model._meta.module_name
        return """<a href="/admin/app/application/%s/?rtn_url=%s" target="_blank"><strong>%s</strong></a>""" \
                % (obj.app.id, reverse('admin:%s_%s_changelist' % info), obj.app.name)
    app_link.allow_tags = True
    app_link.short_description = _("app")

    class Media:
        js = ("applist/js/applist.js",)


def _get_boot_app_types():
    boot_app_type_choices = [('', '---------'), ('add_new_type', _('add new type'))]
    types = BootApp.objects.values('boot_app_type').distinct()
    for item in types:
        t = item['boot_app_type']
        if t:
            boot_app_type_choices.append((t, t))
    return tuple(boot_app_type_choices)


class BootAppAdmin(BootAppAdmin):
    list_display = ('order', 'boot_app_type', 'app_id', 'app_link', 'version', 'full_category', 'rate', 'click_count', 'download_count', \
            'reviews_count', 'modified_time', 'has_icon', 'published', 'review_status', 'sync_status')
    list_display_links = ('app_id',)
    list_filter = ('boot_app_type', 'sync_status', 'review_status','published')

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['boot_app_type'].choices = _get_boot_app_types()
        return super(BootAppAdmin, self).render_change_form(request, context, *args, **kwargs)

    def versions_link(self, obj):
        return """<a href="/admin/utilities/appversionlist/?app__exact=%s" id="versions_%s" onclick="return showRelatedObjectLookupPopup(this);">
                    <strong>%s</strong>
                </a>""" % (obj.app.id, obj.id, obj.versions_count())
    versions_link.allow_tags = True
    versions_link.short_description = _("versions")

    def app_link(self, obj):
        info = self.model._meta.app_label, self.model._meta.module_name
        return """<a href="/admin/app/application/%s/?rtn_url=%s" target="_blank"><strong>%s</strong></a>""" \
                % (obj.app.id, reverse('admin:%s_%s_changelist' % info), obj.app.name)
    app_link.allow_tags = True
    app_link.short_description = _("app")

    class Media:
        js = ("applist/js/applist.js",)


class TopApplicationAdmin(TopAppAdmin):
    list_display = ('order', 'app_id', 'app_link', 'version', 'full_category', 'rate', 'click_count', 'download_count', \
            'reviews_count', 'modified_time', 'has_icon', 'published', 'review_status', 'sync_status', 'app_status')
    list_display_links = ('app_id',)
    list_filter = ('sync_status', 'review_status','published')

    def app_status(self,obj):
        is_published = obj.app.published
        if is_published == 0:
            txt = _("off shelve")
        else:
            txt = _("Ok")
        return txt
    app_status.allow_tags = True
    app_status.short_description = _("app status")

    def versions_link(self, obj):
        return """<a href="/admin/utilities/appversionlist/?app__exact=%s" id="versions_%s" onclick="return showRelatedObjectLookupPopup(this);">
                    <strong>%s</strong>
                </a>""" % (obj.app.id, obj.id, obj.versions_count())
    versions_link.allow_tags = True
    versions_link.short_description = _("versions")

    def app_link(self, obj):
        info = self.model._meta.app_label, self.model._meta.module_name
        return """<a href="/admin/app/application/%s/?rtn_url=%s" target="_blank"><strong>%s</strong></a>""" \
                % (obj.app.id, reverse('admin:%s_%s_changelist' % info), obj.app.name)
    app_link.allow_tags = True
    app_link.short_description = _("app")

    def queryset(self, request):
        return super(TopApplicationAdmin, self).queryset(request).filter(app__category__exact=self.category)

    def has_sync_to_permission(self, request, obj=None):
        return True

    class Media:
        js = ("applist/js/applist.js",)


class ApplicationTopAppAdmin(TopApplicationAdmin):
    form = ApplicationTopAppForm

    def __init__(self, *args, **kwargs):
        self.category = get_category(ugettext('Application'))    # Category should be initialized first
        super(ApplicationTopAppAdmin, self).__init__(*args, **kwargs)


class GameTopAppAdmin(TopApplicationAdmin):
    form = GameTopAppForm

    def __init__(self, *args, **kwargs):
        self.category = get_category(ugettext('Game'))
        super(GameTopAppAdmin, self).__init__(*args, **kwargs)


class ReadingTopAppAdmin(TopApplicationAdmin):
    form = ReadingTopAppForm

    def __init__(self, *args, **kwargs):
        self.category = get_category(ugettext('Reading'))
        super(ReadingTopAppAdmin, self).__init__(*args, **kwargs)


class MusicVideoTopAppAdmin(TopApplicationAdmin):
    form = MusicVideoTopAppForm

    def __init__(self, *args, **kwargs):
        self.category = get_category(ugettext('Music & Video'))
        super(MusicVideoTopAppAdmin, self).__init__(*args, **kwargs)


class TianYiKuWanItemAdmin(KuWanItemAdmin):
    form = KuWanItemAdminForm

    def has_sync_to_permission(self, request, obj=None):
        return True

    class Media:
        js = ("applist/js/applist.js",)

custom_site.register(BootApp, BootAppAdmin)
custom_site.register(PreparedApp, PreparedAppAdmin)
custom_site.register(GameTopApp, GameTopAppAdmin)
custom_site.register(ReadingTopApp, ReadingTopAppAdmin)
custom_site.register(MusicVideoTopApp, MusicVideoTopAppAdmin)
custom_site.register(ApplicationTopApp, ApplicationTopAppAdmin)
custom_site.register(NewestRecommendApp, NewestRecommendedAppAdmin)
custom_site.register(HottestRecommendApp, HottestRecommendedAppAdmin)
custom_site.register(MatchestRecommendApp, MatchestRecommendedAppAdmin)
custom_site.register(HomeNewRecommendApp, HomeNewRecommendedAppAdmin)
custom_site.register(TianYiKuWanItem, TianYiKuWanItemAdmin)
