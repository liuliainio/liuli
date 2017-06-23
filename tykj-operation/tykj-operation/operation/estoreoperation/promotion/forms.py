from django import forms
from django.utils.translation import ugettext_lazy as _
from estoreoperation.promotion.models import Activity, LoginPicture


class ActivityAdminForm(forms.ModelForm):

    def clean(self):
        super(ActivityAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        # check icon_url and icon_path
        if not cleaned_data.get('icon_url', None) and not cleaned_data.get('icon_path', None):
            self._errors['icon_url'] = self.error_class([_('Icon url and icon path can not both be None.')])

        return cleaned_data

    class Meta:
        model = Activity


class LoginPictureAdminForm(forms.ModelForm):

    def clean(self):
        super(LoginPictureAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        # check url and path
        if not cleaned_data.get('url', None) and not cleaned_data.get('path', None):
            self._errors['url'] = self.error_class([_('Url and path can not both be None.')])

        return cleaned_data

    class Meta:
        model = LoginPicture
