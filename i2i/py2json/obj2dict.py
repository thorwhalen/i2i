from __future__ import division

from __future__ import division

import re
from copy import copy


def kind_of_type(obj_type):
    return obj_type.__module__ + '.' + obj_type.__name__


def kind_of_obj(obj):
    return kind_of_type(type(obj))


class ApplyDictOf(object):
    pass


apply_dict_of = ApplyDictOf()


class Obj2Dict(object):
    def __init__(self, to_data_for_kind=None, from_data_for_kind=None):
        if to_data_for_kind is None:
            to_data_for_kind = {}
        if from_data_for_kind is None:
            from_data_for_kind = {}
        to_data_for_kind = copy(to_data_for_kind)

        for k, v in to_data_for_kind.items():
            if isinstance(k, type):
                to_data_for_kind[kind_of_type(k)] = to_data_for_kind.pop(k)

        from_data_for_kind = copy(from_data_for_kind)
        for k, v in from_data_for_kind.items():
            if isinstance(k, type):
                from_data_for_kind[kind_of_type(k)] = from_data_for_kind.pop(k)

        self.to_data_for_kind = to_data_for_kind
        self.from_data_for_kind = from_data_for_kind

    def kind_and_data_of_obj(self, obj):
        kind = kind_of_obj(obj)
        if kind in self.to_data_for_kind:
            return kind, self.to_data_for_kind[kind](obj)
        else:
            return kind, obj

    def obj_of_kind_and_data(self, kind, data):
        if kind.startswith('__builtin__'):
            return data
        elif kind in self.from_data_for_kind:
            return self.from_data_for_kind[kind](data)
        else:
            return apply_dict_of

    def obj_of_kind_data_dict(self, kind_data_dict):
        return self.obj_of_kind_and_data(kind=kind_data_dict['kind'], data=kind_data_dict['data'])

    def dict_of(self, obj, attr_filt=None):
        if attr_filt is None:
            attr_filt = lambda attr: True
        elif isinstance(attr_filt, (list, tuple, set)):
            attr_inclusion_set = set(attr_filt)
            attr_filt = lambda attr: attr in attr_inclusion_set
        elif isinstance(attr_filt, str):
            if attr_filt == 'underscore_suffixed':
                attr_filt = lambda attr: attr.endswith('_')
            else:
                attr_pattern = re.compile(attr_filt)
                attr_filt = attr_pattern.match
        else:
            assert callable(attr_filt), \
                "Don't know what to do with that kind of attr_filt: {}".format(attr_filt)

        d = dict()
        for k in filter(attr_filt, vars(obj)):
            attr_obj = getattr(obj, k)
            kind, data = self.kind_and_data_of_obj(attr_obj)
            if data is not apply_dict_of:
                d[k] = {'kind': kind, 'data': data}
            else:
                d[k] = {'kind': kind, 'data': self.dict_of(data, attr_filt)}

        return {'kind': kind_of_obj(obj), 'data': d}

        # def obj_of(self, obj_dict):
