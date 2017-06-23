from django import forms
from django.utils.translation import ugettext_lazy as _
from estoreoperation.update.models import UpdateApp


class UpdateAppAdminForm(forms.ModelForm):

    def clean(self):
        super(UpdateAppAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        # check download_url and download_path
        #if not cleaned_data.get('download_url', None) and not cleaned_data.get('download_path', None):
            #self._errors['download_url'] = self.error_class([_('Download url and download path can not both be None.')])
        download_url = cleaned_data.get('download_url',None)
        package_size = cleaned_data.get('package_size',None)
        download_path = cleaned_data.get('download_path',None)
        if download_url:
            if download_url.endswith('apk') and not package_size and not download_path:
                self._errors['package_size'] = self.error_class([_('Size can not be empty when use download_url.')])
        return cleaned_data

    class Meta:
        model = UpdateApp
