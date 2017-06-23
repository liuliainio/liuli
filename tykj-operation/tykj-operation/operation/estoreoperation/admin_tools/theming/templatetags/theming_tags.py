"""
Theming template tags.

To load the theming tags just do: ``{% load theming_tags %}``.
"""

from django import template
from django.conf import settings
from admin_tools.utils import get_media_url

register = template.Library()

def render_theming_css():
    """
    Template tag that renders the needed css files for the theming app.
    """
    css = getattr(settings, 'ADMIN_TOOLS_THEMING_CSS', False)
    if css:
        css = '/'.join([get_media_url(), css])
    else:
        css = '/'.join([get_media_url(), 'admin_tools', 'css', 'theming.css'])
    return '<link rel="stylesheet" type="text/css" media="screen" href="%s" />' % css
register.simple_tag(render_theming_css)


def submit_line(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    return {
        'onclick_attrib': (opts.get_ordered_objects() and change
                            and 'onclick="submitOrderForm();"' or ''),
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and (change or context['show_delete'])),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and
                            not is_popup and (not save_as or context['add']),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'show_save_and_sync': not is_popup and context['has_sync_to_permission'] or (context.get('is_sync_button_show',False)),
        'is_popup': is_popup,
        'show_save': True
    }
submit_line = register.inclusion_tag('admin/submit_line.html', takes_context=True)(submit_line)
