#! -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from estoreoperation.app.models import Application
from estorecore.utils.storages import get_package_name_from_temp_file


class NewAppAdminForm(forms.ModelForm):

    def clean(self):
        super(NewAppAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        download_files = [v for k, v in self.files.iteritems() if k.find('download_path') != -1]
        if download_files:
            try:
                temp_file = download_files[0]
                pn = get_package_name_from_temp_file(temp_file)
                if not pn:
                    self._errors['name'] = self.error_class([_('Unpack APK file failed.')])
                else:
                    apps = Application._base_manager.filter(package_name=pn)
                    if apps and not self.data['versions-0-id']:
                        self._errors['name'] = self.error_class([_('The application with same package name exists, %(app_name)s%(is_hided)s, app_id: %(app_id)d.') \
                                % {'app_name': apps[0].name, 'is_hided': _('(hided)') if apps[0].hided else '', 'app_id': apps[0].id}])
            except Exception:
                self._errors['name'] = self.error_class([_('Save APK file failed.')])
        return cleaned_data

    class Meta:
        model = Application
