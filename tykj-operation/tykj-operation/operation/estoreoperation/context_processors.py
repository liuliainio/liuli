import re


def url_name(request):
    url_regex = re.compile(r'^/admin/([^/]+)/.*', re.I)
    # current_url = resolve(request.path_info).url_name
    m = url_regex.search(request.get_full_path())
    url_name = m.group(1) if m else ''
    return {'url_name': url_name}
