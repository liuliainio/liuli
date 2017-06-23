import datetime
from django.contrib.admin.options import ModelAdmin
from django.utils.translation import ugettext_lazy as _
from estorecore.admin.sites import custom_site
from estorecore.admin import EntityModelAdmin,  CommonBaseAdmin
from estoreoperation.promotion.models import Feedback, LoginPicture, LocalEntry
from estoreoperation.promotion.forms import ActivityAdminForm, LoginPictureAdminForm


class ActivityAdmin(EntityModelAdmin, CommonBaseAdmin):
    form = ActivityAdminForm
    list_editable = ('order', 'published')
    list_display = ('title', 'id', 'description', 'start_date', 'end_date', 'pub_date', \
            'icon_path', 'status', 'tag', 'type', 'attr', 'modified_time', 'order', 'published', 'review_status')
    list_per_page = 50
    custom_group = True
    list_filter = ['status', 'review_status', 'tag','published']
    search_fields = ['title', 'description']
    ordering = ('-order',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('title', 'description', 'icon_path', 'large_icon_path', 'large_icon_url', 'tag'),
                }),
            (_('Date'), {
                'fields': ('start_date', 'end_date', 'pub_date'),
                }),
            (_('Type'), {
                'fields': ('type', 'attr'),
                }),
            (_('Status'), {
                'fields': ('status', 'published', 'review_status'),
                }),
            )

    def queryset(self, request):
        filtered_queryset = super(ActivityAdmin, self).queryset(request)
        return self.post_queryset(request, filtered_queryset)

    def save_model(self, request, obj, form, change):
        pre_save_status = self.pre_save_model(request, obj, form, change)
        if not pre_save_status:
            self.message_user(request, _("Fail to pre save model."))
            return
        super(ActivityAdmin, self).save_model(request, obj, form, change)

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['start_date'].initial = datetime.datetime.now()
        context['adminform'].form.fields['pub_date'].initial = datetime.datetime.now()
        return super(ActivityAdmin, self).render_change_form(request, context, *args, **kwargs)


class LoginPictureAdmin(EntityModelAdmin, CommonBaseAdmin):
    form = LoginPictureAdminForm
    list_editable = ('is_default', 'published')
    list_display = ('name', 'path', 'start_date', 'end_date', 'is_default', 'modified_time', 'published', 'sync_status')
    list_per_page = 50
    list_filter = ['is_default', 'review_status','published']
    search_fields = ['name']
    ordering = ('-modified_time',)
    custom_group = True
    fieldsets = (
            (_('Basic'), {
                'fields': ('name', 'path', 'search_keyword', 'home_banner'),
                }),
            (_('Date'), {
                'fields': ('start_date', 'end_date'),
                }),
            (_('Type'), {
                'fields': ('type', 'attr'),
                }),
            (_('Status'), {
                'fields': ('is_default', 'published', 'review_status'),
                }),
            )

    def queryset(self, request):
        filtered_queryset = super(LoginPictureAdmin, self).queryset(request)
        return self.post_queryset(request, filtered_queryset)

    def save_model(self, request, obj, form, change):
        pre_save_status = self.pre_save_model(request, obj, form, change)
        if not pre_save_status:
            self.message_user(request, _("Fail to pre save model."))
            return
        super(LoginPictureAdmin, self).save_model(request, obj, form, change)

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['start_date'].initial = datetime.datetime.now()
        return super(LoginPictureAdmin, self).render_change_form(request, context, *args, **kwargs)


class FeedbackAdmin(EntityModelAdmin):
    list_display = ('id', 'user_id', 'source', 'content', 'created_time')
    list_per_page = 50
    search_fields = ['content']
    list_filter = ['source']
    ordering = ('-created_time',)

    special_exclude = ()
    special_readonly = ()

    def save_model(self, request, obj, form, change):
        obj.app_key = request.user.get_profile().app_key.unique_token
        obj.save()

    def queryset(self, request):
        query_set = ModelAdmin.queryset(self, request)
        user = request.user
        if user.is_superuser:
            return query_set
        return query_set.filter(app_key__exact=user.get_profile().app_key.unique_token)

    def save_formset(self, request, form, formset, change):
        if request.method == "POST":
            objs = formset.save(commit=False)
            for obj in objs:
                obj.save()
            formset.save_m2m()

    def get_actions(self, request):
        actions = super(FeedbackAdmin, self).get_actions(request)
        if 'delete_selected_items' in actions:
            del actions['delete_selected_items']
        return actions


class LocalEntryAdmin(EntityModelAdmin):
    list_editable = ('published', 'order')
    list_display_links = ('name', 'id')
    list_display = ('id', 'order', 'name', 'icon_path', 'action', 'value', 'parameter', 'modified_time', 'published', 'sync_status')
    list_per_page = 50
    list_filter = ['review_status','published']
    search_fields = ['name']
    ordering = ('-modified_time',)
    fieldsets = (
            (_('Basic'), {
                'fields': ('name', 'icon_path', 'action', 'value', 'parameter', 'condition'),
                }),
            (_('Status'), {
                'fields': ('published', 'review_status'),
                }),
            )

custom_site.register(LocalEntry, LocalEntryAdmin)
custom_site.register(Feedback, FeedbackAdmin)
custom_site.register(LoginPicture, LoginPictureAdmin)
