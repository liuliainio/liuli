#-*- coding: utf-8 -*-
'''
Created on Nov 26, 2013

@author: gmliao
'''


def clean_url(url, params_to_remove):
    idx = url.find('?')
    params_to_remove = params_to_remove or []
    path, param = None, {}
    if idx != -1:
        path = url[:idx]
        param_ = url[idx + 1:].split('&')
        for p in param_:
            if p.find('=') != -1:
                k, v = p.split('=')
            else:
                k, v = p, ''
            if k and not k in params_to_remove:
                param[k] = v
        sorted_keys = sorted(param.keys())
        return '%s?%s' % (path, '&'.join(['%s=%s' % (k, param[k]) for k in sorted_keys]))
    return url


def clean_url_from_file(params_to_remove):
    urls = []
    for line in file('urls'):
        if line and line.strip():
            urls.append(clean_url(line.strip(), params_to_remove))
    return urls


if __name__ == '__main__':
    urls = clean_url_from_file(['uid', 'abi', 'usertype', 'ver', 'from', 'operator',
                                'network', 'pkname', 'country', 'cen', 'gms', 'psize', 'f',
                                'platform_version_id', 'firstdoc', 'pu', 'language', 'apn', ])
    urls = set(urls)
    urls = list(urls)
    urls = sorted(filter(lambda url: url.find('pn=') != -1, urls))
    for u in urls:
        print u




