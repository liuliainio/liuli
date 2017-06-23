#-*- coding: utf-8 -*-
'''
Created on Nov 28, 2013

@author: gmliao
'''


def find_attr(json_obj, attr_name, attr_type):
    attr_values = []
    if isinstance(json_obj, dict):
        if attr_name in json_obj and isinstance(json_obj[attr_name], attr_type):
            attr_values.append(json_obj[attr_name])
        for v in json_obj.values():
            for value in find_attr(v, attr_name, attr_type):
                attr_values.append(value)
        return attr_values
    elif isinstance(json_obj, list):
        for v in json_obj:
            for value in find_attr(v, attr_name, attr_type):
                attr_values.append(value)
        return attr_values
    else:
        return attr_values






