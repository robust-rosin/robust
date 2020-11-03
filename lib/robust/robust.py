# -*- coding: utf-8 -*-
__all__ = ('ROBUST',)

import os
import typing as t

import attr


@attr.s
class ROBUST:
    directory: str = attr.ib(converter=os.path.abspath)
    files: t.AbstractSet[str] = attr.ib(repr=False, init=False)

    @staticmethod
    def _locate_bug_files(directory: str) -> t.AbstractSet[str]:
        output: t.Set[str] = set()
        for root, _dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.bug'):
                    output.add(os.path.join(root, filename))
        return output

    def __attrs_post_init__(self) -> None:
        self.files = self._locate_bug_files(self.directory)
