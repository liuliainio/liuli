from django import forms
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from estorecore.utils import safe_cast
from estorecore.models.constants import PUSH_MESSAGE_ACTIONS
from estorecore.admin.fields import NotValidateChoiceField, NotValidateMultipleChoiceField
from estoreoperation.push.models import Message
from estoreoperation.app.models import Application, CategorySubject
from estorecore.models.constants import TG_OPERATORS, TG_CITIES, TG_GENDERS, TG_MARRIAGE_STATUS, TG_AGES, TG_MSG_GROUPS


class PushMessageAdminForm(forms.ModelForm):
    tg_msg_group = NotValidateChoiceField(choices=sorted(list(TG_MSG_GROUPS.to_choices())), required=False, \
            label=_('target message group'), help_text=_('if no one is selected, means no group'))
    tg_device = forms.CharField(required=False, label=_('target device'), \
            help_text=_('use "," to split when add more than one device, if no one is targeted, means all devices. example: zte,htc'))
    tg_sys_version = forms.CharField(required=False, label=_('target system version'), \
            help_text=_('use "," to split when add more than one system version, if no one is targeted, means all system versions. example: 15,16'))
    tg_screen_size = forms.CharField(required=False, label=_('target screen size'), \
            help_text=_('use "," to split when add more than one screen size, if no one is targeted, means all screen sizes. example: 800x600,1024x800'))
    tg_operator = NotValidateMultipleChoiceField(choices=sorted(list(TG_OPERATORS.to_choices())), required=False, widget=forms.CheckboxSelectMultiple(), \
            label=_('target operator'), help_text=_('if no one is selected, means all operators'))
    tg_city = NotValidateMultipleChoiceField(choices=sorted(list(TG_CITIES.to_choices())), required=False, widget=forms.CheckboxSelectMultiple(), \
            label=_('target city'), help_text=_('if no one is selected, means all cities'))
    tg_installed_app = forms.IntegerField(required=False, \
            label=_('target installed app'), help_text=_('target installed app'))
    tg_uninstalled_app = forms.IntegerField(required=False, \
            label=_('target uninstalled app'), help_text=_('target uninstalled app'))
    tg_recently_installed_app = forms.IntegerField(required=False, \
            label=_('target recently installed app'), help_text=_('target recently installed app'))
    tg_frequently_used_app = forms.IntegerField(required=False, \
            label=_('target frequently used app'), help_text=_('target frequently used app'))
    tg_to_activate_app = forms.IntegerField(required=False, \
            label=_('target activated app'), help_text=_('target activated app'))
    tg_expired_app = forms.IntegerField(required=False, \
            label=_('target expired app'), help_text=_('target expired app'))
    tg_gender = NotValidateMultipleChoiceField(choices=sorted(list(TG_GENDERS.to_choices())), required=False, widget=forms.CheckboxSelectMultiple(), \
            label=_('target gender'), help_text=_('if no one is selected, means all genders'))
    tg_marriage_status = NotValidateMultipleChoiceField(choices=sorted(list(TG_MARRIAGE_STATUS.to_choices())), required=False, widget=forms.CheckboxSelectMultiple(), \
            label=_('target marraige status'), help_text=_('if no one is selected, means all marriage status'))
    tg_age = NotValidateMultipleChoiceField(choices=sorted(list(TG_AGES.to_choices())), required=False, widget=forms.CheckboxSelectMultiple(), \
            label=_('target age'), help_text=_('if no one is selected, means all ages'))
    tg_keyword = forms.CharField(required=False, label=_('target keyword'), \
            help_text=_('target keyword help text'))
    tg_phone = forms.CharField(widget=forms.Textarea(attrs={'width': "100%", 'cols': "300", 'rows': "10", }), \
            required=False, label=_('target phone'), help_text=_('target phone number, if no one is targeted, means all, example: 123456789,987654321'))

    extra_repeat_time = forms.IntegerField(required=False, label=_('repeat time (launch background)'), help_text=_('please input an integer.'))
    extra_act_hour = forms.IntegerField(required=False, label=_('action hour (launch background)'), help_text=_('please input an integer, should be in [0, 23].'))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            initial = kwargs.get('initial', {})
            if instance.targets:
                initial.update(simplejson.loads(instance.targets))
            if instance.extra_infos:
                for key, value in simplejson.loads(instance.extra_infos).items():
                    initial['extra_%s' % key] = value
            kwargs['initial'] = initial
        super(PushMessageAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        tg_infos = {}
        extra_infos = {}
        for key, value in cleaned_data.items():
            if key.startswith('tg_'):
                tg_infos[key] = value
            elif key.startswith('extra_'):
                extra_infos[key.replace('extra_', '')] = value
        self.instance.targets = simplejson.dumps(tg_infos)
        self.instance.extra_infos = simplejson.dumps(extra_infos)
        return super(PushMessageAdminForm, self).save(commit=commit)

    def clean(self):
        super(PushMessageAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        action, value = cleaned_data.get('action'), cleaned_data.get('value')

        for field in ('tg_installed_app', 'tg_uninstalled_app', 'tg_recently_installed_app', 'tg_frequently_used_app', 'tg_to_activate_app', 'tg_expired_app'):
            app_id = cleaned_data.get(field, None)
            if app_id and safe_cast(app_id, long) is None:
                self._errors[field] = self.error_class([_('Input value should be an intger.')])
                break
            apps = Application.objects.filter(pk__exact=app_id)
            if app_id and not apps:
                self._errors[field] = self.error_class([_('Please select an exist application.')])
                break
            elif app_id and not apps[0].review_status:
                self._errors[field] = self.error_class([_('Please select reviewed application.')])
                break
            cleaned_data['%s_pn' % field] = apps[0].package_name if app_id and apps else ""

        if action not in (PUSH_MESSAGE_ACTIONS.URL, PUSH_MESSAGE_ACTIONS.SHORT_CUT_URL) and safe_cast(value, int) is None:
            self._errors['value'] = self.error_class([_('Input value should be an intger.')])
            del cleaned_data["value"]
            return cleaned_data

        if action in (PUSH_MESSAGE_ACTIONS.APP_DETAILES_PAGE, PUSH_MESSAGE_ACTIONS.SHORT_CUT_DETAIL_PAGE, \
                PUSH_MESSAGE_ACTIONS.SHORT_CUT_DOWNLOAD_APP, PUSH_MESSAGE_ACTIONS.DOWNLOAD_APP, \
                PUSH_MESSAGE_ACTIONS.DOWNLOADB, PUSH_MESSAGE_ACTIONS.LAUNCHB):
            if safe_cast(value, int) is None:
                apps = Application.objects.filter(package_name__exact=value)
            else:
                apps = Application.objects.filter(pk__exact=value)
            if not apps:
                self._errors['value'] = self.error_class([_('Please select an exist application.')])
                del cleaned_data["value"]
            elif not apps[0].review_status:
                self._errors['value'] = self.error_class([_('Please select reviewed application.')])
                del cleaned_data["value"]
        elif action == PUSH_MESSAGE_ACTIONS.SUBJECT_INFO:
            subjects = CategorySubject.objects.filter(pk__exact=value)
            if not subjects:
                self._errors['value'] = self.error_class([_('Please select an exist subject.')])
                del cleaned_data["value"]
            elif not subjects[0].review_status:
                self._errors['value'] = self.error_class([_('Please select reviewed subject.')])
                del cleaned_data["value"]

        return cleaned_data

    class Meta:
        model = Message
