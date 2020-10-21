# -*- coding: utf-8 -*-
"""
This module defines the YAML format that is used by ROBUST bug descriptions.
"""
__all__ = ('yaml',)

import typing as t

import ruamel.yaml


def _represent_none_as_null(self: ruamel.yaml.representer.Representer,
                            data: t.Any
                            ) -> t.Any:
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')


yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True  # type: ignore
yaml.representer.add_representer(type(None), _represent_none_as_null)
yaml.indent(mapping=2, sequence=4, offset=2)
