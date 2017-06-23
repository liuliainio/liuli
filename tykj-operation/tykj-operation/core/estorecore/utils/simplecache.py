# -*- coding: utf-8 -*-
from django.core.cache import cache

def _build_cache_key(key_vars):
    if not isinstance(key_vars, list):
        key_vars = [key_vars]
    key_vars = [var.encode('utf8') if isinstance(var, unicode) else str(var) for var in key_vars]
    return '\t'.join(key_vars)

def cached_query(key_vars, query_func, query_func_state = None, timeout = 300, return_cache_hit_status = False):
    key = _build_cache_key(key_vars)

    value = cache.get(key)

    cache_hit = 0 if value is None else 1
    if value is None and query_func is not None:
        value = query_func(query_func_state)
        cache.set(key, value, timeout)

    if return_cache_hit_status:
        value = (value, cache_hit)

    return value
