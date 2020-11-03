# -*- coding: utf-8 -*-
__all__ = ('BugDescription', 'ROBUST')

import os
import typing as t

import attr

from .yaml import yaml


@attr.s
class BugSection:
    bug: 'BugDescription' = attr.ib()

    @property
    def phase(self) -> str:
        return self.bug.yaml['bug']['phase']

    @property
    def specificity(self) -> str:
        return self.bug.yaml['bug']['specificity']

    @property
    def architectural_location(self) -> str:
        return self.bug.yaml['bug']['architectural-location']

    @property
    def application(self) -> str:
        return self.bug.yaml['bug']['application']

    @property
    def task(self) -> str:
        return self.bug.yaml['bug']['task']

    @property
    def subsystem(self) -> str:
        return self.bug.yaml['bug']['subsystem']

    @property
    def package(self) -> str:
        return self.bug.yaml['bug']['package']

    @property
    def languages(self) -> t.AbstractSet[str]:
        return set(self.bug.yaml['bug']['languages'])

    @property
    def detected_by(self) -> str:
        return self.bug.yaml['bug']['detected-by']

    @property
    def reported_by(self) -> str:
        return self.bug.yaml['bug']['reported-by']

    @property
    def issue(self) -> str:
        return self.bug.yaml['bug']['issue']


@attr.s
class FixSection:
    bug: 'BugDescription' = attr.ib()

    @property
    def pull_request(self) -> str:
        return self.bug.yaml['fix']['pull-request']

    @property
    def license(self) -> t.AbstractSet[str]:
        return self.bug.yaml['fix']['license']

    @property
    def fix_in(self) -> t.AbstractSet[str]:
        return self.bug.yaml['fix']['fix-in']

    @property
    def languages(self) -> t.AbstractSet[str]:
        return self.bug.yaml['fix']['languages']


@attr.s
class BugDescription:
    filename: str = attr.ib()
    yaml: t.Dict[str, t.Any] = attr.ib(repr=False, eq=False)

    @classmethod
    def load(cls, filename: str) -> 'BugDescription':
        with open(filename, 'r') as f:
            yaml_ = yaml.load(f)
        return BugDescription(filename, yaml_)

    @property
    def id(self) -> str:
        return self.yaml['id']

    @property
    def description(self) -> str:
        return self.yaml['description']

    @property
    def title(self) -> str:
        return self.yaml['title']

    @property
    def severity(self) -> str:
        return self.yaml['severity']

    @property
    def keywords(self) -> t.AbstractSet[str]:
        return set(self.yaml['keywords'])

    @property
    def links(self) -> t.AbstractSet[str]:
        return set(self.yaml['links'])

    @property
    def bug(self) -> BugSection:
        return BugSection(self)

    @property
    def fix(self) -> FixSection:
        return FixSection(self)


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
