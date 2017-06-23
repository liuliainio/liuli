from django import forms
from django.forms import widgets
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from estorecore.utils import safe_cast
from estorecore.models.constants import APP_RATES, RECOMMEND_TYPES, RICHITEM_TYPE, GAME_APP_DISPLAY_MODE
from estoreoperation.admin.applist.models import AppListItem, CategoryRecommendApp, \
        NewestRecommendApp, HottestRecommendApp, MatchestRecommendApp, HomeNewRecommendApp, \
        TopApp, ApplicationTopApp, GameTopApp, ReadingTopApp, MusicVideoTopApp


class AppListItemAdminForm(forms.ModelForm):
    extra_kuwan_price = forms.DecimalField(required=False, label=_('kuwan price'), help_text=_('the price of kuwan item.'))
    extra_editor_category = forms.CharField(required=False, label=_('editor category'), help_text=_('input editor category name.'))
    extra_added_price = forms.DecimalField(required=False, min_value=0, label=_('value added price'), help_text=_('Please input value-added price.'))
    extra_added_desc = forms.CharField(required=False, label=_('app desc'),widget=widgets.Textarea, help_text=_('Please input app description.'))
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            initial = kwargs.get('initial', {})
            if instance.extra_infos:
                for key, value in simplejson.loads(instance.extra_infos).items():
                    initial['extra_%s' % key] = value
            kwargs['initial'] = initial
        super(AppListItemAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        extra_infos = {}
        for key, value in cleaned_data.items():
            if key.startswith('extra_'):
                extra_infos[key.replace('extra_', '')] = value
        self.instance.extra_infos = simplejson.dumps(extra_infos) if extra_infos else None
        return super(AppListItemAdminForm, self).save(commit=commit)

    def clean(self):
        super(AppListItemAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        app_list = cleaned_data['app_list']
        app = cleaned_data.get('app', None)
        if not app:
            self._errors['app'] = self.error_class([_('App should not be None.')])
            return cleaned_data
        if not app.review_status or not app.published:
            self._errors['app'] = self.error_class([_('Please select reviewed application.')])
            return cleaned_data

        app_exists = AppListItem.objects.filter(app=app, app_list=app_list).exists()
        if not self.initial and app_exists:
            self._errors['app'] = self.error_class([_('item with app id with %(id)s exists in the list') % {'id': app.id}])
        return cleaned_data

    class Meta:
        model = AppListItem


class BannerAppListItemAdminForm(forms.ModelForm):
    type_choices = []
    for k, v in RICHITEM_TYPE.to_dict().items():
        if k not in (RICHITEM_TYPE.TIANYI_KUWAN, RICHITEM_TYPE.TIANYI_QNW):
            type_choices.append((k, v))
    type = forms.ChoiceField(choices=tuple(type_choices), label=_('type'))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            initial = kwargs.get('initial', {})
            if instance.extra_infos:
                for key, value in simplejson.loads(instance.extra_infos).items():
                    initial['extra_%s' % key] = value
            kwargs['initial'] = initial
        super(BannerAppListItemAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        extra_infos = {}
        for key, value in cleaned_data.items():
            if key.startswith('extra_'):
                extra_infos[key.replace('extra_', '')] = value
        self.instance.extra_infos = simplejson.dumps(extra_infos) if extra_infos else None
        return super(BannerAppListItemAdminForm, self).save(commit=commit)

    def clean(self):
        super(BannerAppListItemAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        app_list = cleaned_data['app_list']
        type = cleaned_data['type']
        attr = cleaned_data['attr']
        for field in ('type', 'attr'):
            if not cleaned_data.get(field, None):
                self._errors[field] = self.error_class([_('This field should not be None.')])

        # check icon_url and icon_path
        if not cleaned_data.get('icon_url', None) and not cleaned_data.get('icon_path', None):
            self._errors['icon_url'] = self.error_class([_('Icon url and icon path can not both be None.')])

        is_exists = AppListItem.objects.filter(app_list=app_list, type=type, attr=attr).exists()
        if not self.initial and is_exists and type and attr:
            self._errors['attr'] = self.error_class([_('item with type: %(type)s, attr: %(attr)s exists in the list' % {'type': type, 'attr': attr})])
        return cleaned_data

    class Meta:
        model = AppListItem


class GameAppListAdminForm(AppListItemAdminForm):
    extra_display_mode = forms.ChoiceField(choices=GAME_APP_DISPLAY_MODE.to_choices(), label=_('display mode'))

    def clean(self):
        super(GameAppListAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data

        # check icon_url and icon_path
        if not cleaned_data.get('icon_url', None) and not cleaned_data.get('icon_path', None):
            self._errors['icon_url'] = self.error_class([_('Icon url and icon path can not both be None.')])
        cleaned_data['extra_display_mode'] = int(cleaned_data['extra_display_mode'])
        return cleaned_data


class WebAppBannerListAdminForm(BannerAppListItemAdminForm):
    type_choices = []
    for k, v in RICHITEM_TYPE.to_dict().items():
        if k == RICHITEM_TYPE.URL:
            type_choices.append((k, v))
    type = forms.ChoiceField(initial=RICHITEM_TYPE.URL, choices=tuple(type_choices), label=_('type'))
    title = forms.CharField(max_length=255, required=True, label=_('title'))
    extra_rate = forms.ChoiceField(choices=APP_RATES, required=True, label=_('rate'))
    extra_views_count = forms.IntegerField(required=True, label=_('views count'))
    extra_app_icon_url = forms.URLField(required=False, label=_('app icon url'), help_text=_('Please input app icon url'))

    def clean(self):
        super(WebAppBannerListAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        views_count = cleaned_data.get('extra_views_count')

        if views_count and safe_cast(views_count, long) is None:
            self._errors['extra_views_count'] = self.error_class([_('Input value should be an intger.')])

        cleaned_data['extra_rate'] = float(cleaned_data['extra_rate'])
        return cleaned_data


class OrderAreaBannerListAdminForm(BannerAppListItemAdminForm):
    type_choices = []
    for k, v in RICHITEM_TYPE.to_dict().items():
        if k in (RICHITEM_TYPE.APP_DETAILES_PAGE, RICHITEM_TYPE.TIANYI_KUWAN, RICHITEM_TYPE.TIANYI_QNW):
            type_choices.append((k, v))
    type = forms.ChoiceField(choices=tuple(type_choices), label=_('type'))
    extra_order_id = forms.IntegerField(required=True, label=_('order ID'), \
            help_text=_('APP ID for app_details_page type, kuwan item id for tianyi_kuwan type, 1 for tianyi quan neng wan type.'))
    extra_order_url = forms.URLField(required=True, label=_('order URL'), help_text=_('web page url of ordering'))
    extra_price = forms.DecimalField(required=True, label=_('price'), help_text=_('the price of app, kuwan item or quan neng wan.'))
    extra_title = forms.CharField(required=True, label=_('title'), help_text=_('the title of app or kuwan item, or "quan neng wan" for tianyi quan neng wan type.'))

    def clean(self):
        super(OrderAreaBannerListAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        order_id = cleaned_data.get('extra_order_id')

        if order_id and safe_cast(order_id, long) is None:
            self._errors['extra_order_id'] = self.error_class([_('Input value should be an intger.')])
        return cleaned_data


class RecommendAppAdminForm(forms.ModelForm):

    def clean(self):
        super(RecommendAppAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        app = cleaned_data.get('app')
        if not app.review_status or not app.published:
            self._errors['app'] = self.error_class([_('Please select reviewed application.')])
            return cleaned_data

        app_exists = CategoryRecommendApp.objects.filter(app=app, type__exact=self.recommend_type).exists()
        if not self.initial and app_exists:
            self._errors['app'] = self.error_class([_('item with app id %(id)s exists in the list') % {'id': app.id}])

        return cleaned_data


class NewestRecommendAppForm(RecommendAppAdminForm):
    recommend_type = RECOMMEND_TYPES.NEWEST

    class Meta:
        models = NewestRecommendApp


class HottestRecommendAppForm(RecommendAppAdminForm):
    recommend_type = RECOMMEND_TYPES.HOTTEST

    class Meta:
        models = HottestRecommendApp


class MatchestRecommendAppForm(RecommendAppAdminForm):
    recommend_type = RECOMMEND_TYPES.MATCHEST

    class Meta:
        models = MatchestRecommendApp


class HomeNewRecommendAppForm(RecommendAppAdminForm):
    recommend_type = RECOMMEND_TYPES.HOME_NEW

    class Meta:
        models = HomeNewRecommendApp


class TopAppAdminForm(forms.ModelForm):

    def clean(self):
        super(TopAppAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        app = cleaned_data.get('app')

        if self.cate_name != app.category.name:
            self._errors['app'] = self.error_class([_('Selected app is not belong to %(cate_name)s.') % {'cate_name': self.cate_name}])
            return cleaned_data
        if not app.review_status or not app.published:
            self._errors['app'] = self.error_class([_('Please select reviewed application.')])
            return cleaned_data

        app_exists = TopApp.objects.filter(app=app).exists()
        if not self.initial and app_exists:
            self._errors['app'] = self.error_class([_('item with app id %(id)s exists in the list') % {'id': app.id}])
        return cleaned_data


class ApplicationTopAppForm(TopAppAdminForm):
    cate_name = _('Application')

    class Meta:
        models = ApplicationTopApp


class GameTopAppForm(TopAppAdminForm):
    cate_name = _('Game')

    class Meta:
        models = GameTopApp


class ReadingTopAppForm(TopAppAdminForm):
    cate_name = _('Reading')

    class Meta:
        models = ReadingTopApp


class MusicVideoTopAppForm(TopAppAdminForm):
    cate_name = _('Music & Video')

    class Meta:
        models = MusicVideoTopApp


class KuWanItemAdminForm(forms.ModelForm):

    def clean(self):
        super(KuWanItemAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        # check icon_url and icon_path
        if not cleaned_data.get('icon_url', None) and not cleaned_data.get('icon_path', None):
            self._errors['icon_url'] = self.error_class([_('Icon url and icon path can not both be None.')])

        return cleaned_data
