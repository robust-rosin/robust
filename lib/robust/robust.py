# -*- coding: utf-8 -*-
__all__ = ('BugDescription', 'ROBUST')

import os
import typing as t

import attr

from .yaml import yaml


@attr.s
class BugDescription:
    filename: str = attr.ib()
    yaml: t.Dict[str, t.Any] = attr.ib(repr=False, eq=False)

    @classmethod
    def load(cls, filename: str) -> 'BugDescription':
        yaml_ = yaml.load(filename)
        return BugDescription(filename, yaml_)


@attr.s
class ROBUST(t.Mapping[str, BugDescription]):
    directory: str = attr.ib(converter=os.path.abspath)
    _descriptions: t.Mapping[str, BugDescription] = \
        attr.ib(repr=False, init=False)

    @classmethod
    def _locate_bug_files(cls, directory: str) -> t.AbstractSet[str]:
        output: t.Set[str] = set()
        for root, _dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.bug'):
                    output.add(os.path.join(root, filename))
        return output

    def __attrs_post_init__(self) -> None:
        files = self._locate_bug_files(self.directory)
        self._descriptions = \
            {filename: BugDescription.load(filename) for filename in files}

    def __iter__(self) -> t.Iterator[str]:
        yield from self._descriptions

    def __getitem__(self, filename: str) -> BugDescription:
        return self._descriptions[filename]

    def __len__(self) -> int:
        return len(self._descriptions)

    def __contains__(self, filename: t.Any) -> bool:
        if not isinstance(filename, str):
            return False
        return filename in self._descriptions
