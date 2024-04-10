#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import operator
from datetime import datetime, timezone
from functools import cached_property
from typing import Any

from flask import current_app, request
from werkzeug.utils import secure_filename

try:
    from flask_wtf import FlaskForm
except ImportError:
    from flask_wtf import Form as FlaskForm

from wtforms import Field
from wtforms.validators import ValidationError

__version__ = "2024.04.10"
FILE_FIELDS = {"FileField", "MultipleFileField"}
NON_VALUE_FIELDS = {"SubmitField"} | FILE_FIELDS
NON_HTML_FIELDS = (
    "SubmitField",
    "CSRFTokenField",
    "HiddenField",
    "FormField",
    "FieldList",
)


def required_if(
    depend_name: str = "",
    op: str = "",
    value: Any = None,
    checks: list = [],
    error_msg: str = "This field is required",
):
    def check_field(form: FlaskForm, field: Field) -> Any:
        data = field.data
        if isinstance(data, str):
            data = data.strip()

        if data:
            return

        checks_ = checks or [(depend_name, op, value)]
        logics = 0
        for dep_name, op_, val in checks_:
            depend_data = getattr(form, dep_name).data
            if isinstance(depend_data, str):
                if field.type != "PasswordField":
                    depend_data = depend_data.strip()

            if depend_data and op_:
                func = getattr(operator, op_, None)
                logic1 = func and func(depend_data, val)
                logic2 = (not func) and getattr(depend_data, op_)(val)
                if logic1 or logic2:
                    logics += 1

        if logics == len(checks_):
            raise ValidationError(error_msg)

    return check_field


class ToppingForm(FlaskForm):
    __lowers__ = []
    __uppers__ = []
    __nostrips__ = []
    __excludes__ = []
    __aliases__ = {}

    def filter_fields(self, field_types: Any, contains: bool = True) -> list:
        if isinstance(field_types, str):
            types = (field_types,)
        else:
            types = field_types

        if contains:
            return [fid.name for fid in self if fid.type in types]

        return [fid.name for fid in self if fid.type not in types]

    @cached_property
    def html_fields(self) -> list:
        return self.filter_fields(NON_HTML_FIELDS, False)

    @cached_property
    def select_fields(self) -> list:
        return self.filter_fields(("SelectField", "SelectMultipleField"))

    @cached_property
    def radio_fields(self) -> list:
        return self.filter_fields("RadioField")

    @cached_property
    def boolean_fields(self) -> list:
        return self.filter_fields("BooleanField")

    @cached_property
    def file_fields(self) -> list:
        return self.filter_fields(("FileField", "MultipleFileField"))

    @cached_property
    def date_fields(self) -> list:
        return self.filter_fields(("DateField", "DateTimeField", "DateTimeLocalField"))

    @cached_property
    def submit_fields(self) -> list:
        return self.filter_fields("SubmitField")

    def get_file(self, fo: Any) -> dict:
        return dict(
            file=fo,
            filename=fo.filename,
            secure_filename=secure_filename(fo.filename),
        )

    def get_files(self, name: str) -> list:
        files = []
        file_names = set()
        for fo in request.files.getlist(name):
            if fo and fo.filename:
                info = self.get_file(fo)
                if info["secure_filename"] not in file_names:
                    files.append(self.get_file(fo))

                file_names.add(info["secure_filename"])

        return files

    def parse_files(self, names: list = []) -> dict:
        data = {}
        for name in names:
            if files := self.get_files(name):
                data[name] = files

        for field in self:
            if field.data and field.type.endswith("FileField"):
                if files := self.get_files(field.name):
                    data[field.name] = files

        return data

    def parse_form(self, box_wrap: bool = False, use_timestamps: bool = False) -> dict:
        lowers = self.get_attrs("lowers")
        uppers = self.get_attrs("uppers")
        nostrips = self.get_attrs("nostrips")
        excludes = self.get_attrs("excludes")
        aliases = self.get_attrs("aliases", is_list=False)
        csrf = current_app.config.get("WTF_CSRF_FIELD_NAME") or "csrf_token"
        if csrf:
            excludes.append(csrf)

        dct = {}
        for field in self:
            name = field.name
            if name in excludes or field.type in NON_VALUE_FIELDS:
                continue

            data = field.data
            if name not in nostrips and field.type != "PasswordField" and isinstance(data, str):
                data = data.strip()

            if data is not None:
                if name in lowers:
                    data = data.lower()
                elif name in uppers:
                    data = data.upper()

            dct[aliases.get(name, name)] = data

        if use_timestamps:
            now = datetime.now(timezone.utc)
            dct.update(created_at=now, updated_at=now)

        if box_wrap:
            try:
                from addict import Dict

                return Dict(dct)
            except ImportError:
                pass

        return dct

    def get_attrs(self, kind: str = "lowers", is_list: bool = True) -> Any:
        attrs_ = [] if is_list else {}
        attr_name = "__{}__".format(kind)
        for kls in self.__class__.__mro__:
            if kls.__name__ == "ToppingForm":
                break

            if is_list:
                attrs_.extend(kls.__dict__.get(attr_name, []))
            else:
                for k, v in kls.__dict__.get(attr_name, {}).items():
                    attrs_.setdefault(k, v)

        return list(set(attrs_)) if is_list else attrs_
