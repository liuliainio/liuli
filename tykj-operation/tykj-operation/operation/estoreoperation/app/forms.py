from django import forms
from django.utils.translation import ugettext_lazy as _
from estorecore.utils.storages import get_package_name_from_temp_file
from estorecore.admin.fields import NotValidateChoiceField
from estorecore.models.constants import CATEGORY_LEVELS, BANNER_IMAGE_AREAS, RICHITEM_TYPE
from estoreoperation.app.models import Category, CategoryFoucsImage, CategorySubject, \
        Application, AppVersion, PreparedApp, BootApp
from estorecore.models.widgets import HyperLinkWidget

class ApplicationAdminForm(forms.ModelForm):

    def clean(self):
        super(ApplicationAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        if self.instance.pk:
            unpublished_reason = cleaned_data.get('unpublished_reason', '').strip()
            published = cleaned_data.get('published', None)
            if not published and not unpublished_reason:
                self._errors['published'] = self.error_class([_('Please input your off shelf reason.')])
                del cleaned_data["published"]
            if published and unpublished_reason:
                cleaned_data['unpublished_reason']=''

        return cleaned_data

    class Meta:
        model = Application


class CategoryAdminForm(forms.ModelForm):

    def clean(self):
        super(CategoryAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        level = cleaned_data.get('level')
        parent_category = cleaned_data.get('parent_category', None)

        # check parent_category
        if level == CATEGORY_LEVELS.CATEGORY and parent_category != None:
            self._errors['parent_category'] = self.error_class([_('Parent category should be None when level is Category.')])
            del cleaned_data["parent_category"]
        elif level == CATEGORY_LEVELS.SUB_CATEGORY and parent_category == None:
            self._errors['parent_category'] = self.error_class([_('Parent category should not be None when level is Sub Category.')])
            del cleaned_data["parent_category"]
        elif level == CATEGORY_LEVELS.SUB_CATEGORY and parent_category.level == CATEGORY_LEVELS.SUB_CATEGORY:
            self._errors['parent_category'] = self.error_class([_('The level of parent category is Sub Category.')])
            del cleaned_data["parent_category"]

        return cleaned_data

    class Meta:
        model = Category


class AppVersionAdminForm(forms.ModelForm):

    #telecom-cnet app download address support delayed to next iteration
    #hyper_download_url = forms.CharField(required=False,widget=HyperLinkWidget(),label=_('hyper link of donload address'))

    def clean(self):
        super(AppVersionAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        related_app = cleaned_data.get('app', None)
        if not related_app:
            self._errors['app'] = self.error_class([_('App should not be None.')])
            return cleaned_data
        download_files = [v for k, v in self.files.iteritems() if k.find('download_path') != -1]
        if download_files:
            try:
                temp_file = download_files[0]
                pn = get_package_name_from_temp_file(temp_file.temporary_file_path())
                if not pn:
                    self._errors['download_path'] = self.error_class([_('Unpack APK file failed.')])
                else:
                    if pn != related_app.package_name and not related_app.package_name.startswith('test.'):
                        apps = Application._base_manager.filter(package_name=pn)
                        if apps:
                            error_info = _("Upload APK's package name is different from app's package name, please add new version to app: \
                                    %(app_name)s%(is_hided)s, app_id: %(app_id)d.") \
                                    % {'app_name': apps[0].name, 'is_hided': _('(hided)') if apps[0].hided else '', 'app_id': apps[0].id}
                        else:
                            error_info = _("Upload APK's package name is different from app's package name, please add new application.")
                        self._errors['download_path'] = self.error_class([error_info])
            except Exception:
                self._errors['download_path'] = self.error_class([_('Save APK file failed.')])
        return cleaned_data

    class Meta:
        model = AppVersion


class CategoryFoucsImageAdminForm(forms.ModelForm):

    def clean(self):
        super(CategoryFoucsImageAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        # check icon_url and icon_path
        if not cleaned_data.get('icon_url', None) and not cleaned_data.get('icon_path', None):
            self._errors['icon_url'] = self.error_class([_('Icon url and icon path can not both be None.')])

        selected_type = cleaned_data.get('type')
        selected_attr = cleaned_data.get('attr')
        if selected_type == RICHITEM_TYPE.APP_DETAILES_PAGE:
            app = Application.objects.filter(pk__exact=int(selected_attr))
            if not app or not app[0].review_status:
                self._errors['attr'] = self.error_class([_('Please select reviewed application.')])
                del cleaned_data['attr']
        elif selected_type == RICHITEM_TYPE.SUBJECT_INFO:
            subject = CategorySubject.objects.filter(pk__exact=int(selected_attr))
            if not subject or not subject[0].review_status:
                self._errors['attr'] = self.error_class([_('Please select reviewed subject.')])
                del cleaned_data['attr']

        return cleaned_data

    class Meta:
        model = CategoryFoucsImage


class PreparedAppAdminForm(forms.ModelForm):

    def clean(self):
        super(PreparedAppAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        app = cleaned_data.get('app')
        if not app.review_status or not app.published:
            self._errors['app'] = self.error_class([_('Please select reviewed application.')])
            return cleaned_data

        app_exists = PreparedApp.objects.filter(app=app).exists()
        if not self.initial and app_exists:
            self._errors['app'] = self.error_class([_('item with app id %(id)s exists in the list') % {'id': app.id}])

        return cleaned_data

    class Meta:
        model = PreparedApp


class BootAppAdminForm(forms.ModelForm):
    boot_app_type = NotValidateChoiceField(label=_('boot app type'), required=True, help_text=_('select add new type to add new one.'))

    def clean(self):
        super(BootAppAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        app = cleaned_data.get('app')
        if not app.review_status or not app.published:
            self._errors['app'] = self.error_class([_('Please select reviewed application.')])
            return cleaned_data

        app_exists = BootApp.objects.filter(app=app).exists()
        if not self.initial and app_exists:
            self._errors['app'] = self.error_class([_('item with app id %(id)s exists in the list') % {'id': app.id}])

        return cleaned_data

    class Meta:
        model = BootApp
