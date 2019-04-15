#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import six
from flask import current_app
try:
    from flask_wtf import FlaskForm
except ImportError:
    from flask_wtf import Form as FlaskForm

__version__ = "0.2.0"


class ToppingForm(FlaskForm):
    __lowers__ = []
    __uppers__ = []
    __nostrips__ = []
    __excludes__ = []

    def parse_form(self):
        lowers = self.get_attrs("lowers")
        uppers = self.get_attrs("uppers")
        nostrips = self.get_attrs("nostrips")
        excludes = self.get_attrs("excludes")
        field_name = current_app.config.get("WTF_CSRF_FIELD_NAME")
        if field_name:
            excludes.append(field_name)

        dct = {}
        for name, field in self._fields.items():
            if name in excludes:
                continue

            data = field.data
            if name in lowers:
                data = data.lower()
            elif name in uppers:
                data = data.upper()

            if name not in nostrips and isinstance(data, six.string_types):
                data = data.strip()

            dct[name] = data

        return dct

    def get_attrs(self, kind="lowers"):
        attrs_ = []
        attr_name = "__{}__".format(kind)
        for kls in self.__class__.__mro__:
            if kls.__name__ == "ToppingForm":
                break

            attrs_.extend(kls.__dict__.get(attr_name, []))

        return list(set(attrs_))
