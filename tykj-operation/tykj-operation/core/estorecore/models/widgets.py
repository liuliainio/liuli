from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Widget, TextInput


class BtnUrlWidget(TextInput):

    def render(self, name, value, attrs=None):
        htmls = []
        id = attrs['id']
        lookup = _('view img') + ''
        htmls.append(super(BtnUrlWidget, self).render(name, value, attrs))
        htmls.append(u'<input type="button" value="' + lookup + '" onclick="popTarget(\'' + id +
            u'\');" id="icon_pop" style="padding:7px 5px;margin-left:8px;" />')

        return mark_safe( u''.join(htmls) )


class HyperLinkWidget(Widget):

    target = "_blank"
    target_link = '#'
    target_name = target_link

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, target=self.target, href=self.target_link, style='display:block;padding-top:10px;')
        if value:
            self.target_name = value

        return mark_safe(u'<a%s>%s</a>' % (self.flatatt(final_attrs),self.target_name))

    def flatatt(self,dict_attrs):
        flat = [u' ']
        for k in dict_attrs:
            flat.append(k + '="' + dict_attrs[k] + '"')

        return u''.join(flat)
