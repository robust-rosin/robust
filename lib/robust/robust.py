# -*- coding: utf-8 -*-
__all__ = ('BugDescription', 'ROBUST')

import os
import typing as t

import attr
import git
import validators

from .yaml import yaml

_URL_PREFIX = 'https://github.com/'
_FORKED_REPOS = (
    'mavros',
    'kobuki',
    'motoman',
    'turtlebot',
    'cob_command_tools',
    'rosdistro',
    'image_pipeline',
    'kobuki_desktop',
    'cob_control',
    'cob_android',
    'yujin_ocs',
    'kobuki_core',
    'geometry2',
    'universal_robot',
    'cob_robots',
    'ros_comm',
)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class BugSection:
    bug: 'BugDescription'

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


@attr.s(auto_attribs=True, frozen=True, slots=True)
class FixCommit:
    repo: str
    hash_: str


@attr.s(auto_attribs=True, frozen=True, slots=True)
class FixSection:
    bug: 'BugDescription'

    def _read_field(self,
                    key: str,
                    expected_type: t.Optional[t.Type] = None,
                    optional: bool = False
                    ) -> t.Any:
        value: t.Any

        try:
            value = self.bug.yaml['fix'][key]
        except KeyError as exc:
            message = (f"{self.bug.filename}: missing 'fix.{key}' "
                        "in bug description")
            raise ValueError(message) from exc

        if value is None:
            if optional:
                return value

            message = (f"{self.bug.filename}: 'fix.{key}' is not optional "
                       "(must not be null)")
            raise ValueError(message)

        if expected_type is not None and not isinstance(value, expected_type):
            message = (f"{self.bug.filename}: 'fix.{key}' has wrong type "
                       f"(expected {expected_type.__name__})")
            raise ValueError(message)

        return value

    @property
    def pull_request(self) -> t.Optional[str]:
        return self._read_field('pull-request', str, optional=True)

    @property
    def license(self) -> t.Optional[t.AbstractSet[str]]:
        licenses = self._read_field('license', list, optional=True)
        return set(licenses)

    @property
    def fix_in(self) -> t.Optional[t.AbstractSet[str]]:
        filenames: t.List[str] = self._read_field('fix-in', list, optional=True)
        return set(filenames)

    @property
    def languages(self) -> t.Optional[t.AbstractSet[str]]:
        languages: t.Optional[t.List[str]] = \
            self._read_field('languages', list, optional=True)
        if languages is None:
            return None
        return set(languages)

    @property
    def commits(self) -> t.AbstractSet[FixCommit]:
        commits: t.Set[FixCommit] = set()
        for commit_dict in self._read_field('commits'):
            print(commit_dict)
            repo = commit_dict['repo']
            hash_ = commit_dict['hash']
            commit = FixCommit(repo, hash_)
            commits.add(commit)
        return commits


@attr.s(auto_attribs=True, slots=True)
class BugDescription:
    filename: str
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
    _forks_directory: str = attr.ib(repr=False, init=False)
    _descriptions: t.Mapping[str, BugDescription] = \
        attr.ib(repr=False, init=False)

    def __attrs_post_init__(self) -> None:
        files = self._locate_bug_files(self.directory)
        self._descriptions = \
            {filename: BugDescription.load(filename) for filename in files}

        self._forks_directory = os.path.join(self.directory, '.forks')
        if not os.path.exists(self._forks_directory):
            os.mkdir(self._forks_directory)

    @classmethod
    def _locate_bug_files(cls, directory: str) -> t.AbstractSet[str]:
        output: t.Set[str] = set()
        for root, _dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.bug'):
                    output.add(os.path.join(root, filename))
        return output

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

    @classmethod
    def _validate_repo_url(cls, url: str) -> None:
        if not url.startswith(_URL_PREFIX):
            error = f"bad repo URL: {url} [must start with {_URL_PREFIX}]"
            raise ValueError(error)

        if not validators.url(url):
            error = f"bad repo URL: {url} [not a valid URL]"
            raise ValueError(error)

    @classmethod
    def _repo_url_to_fork_url(cls, url: str) -> str:
        cls._validate_repo_url(url)
        url_basename = os.path.basename(url[len(_URL_PREFIX):])

        if url_basename not in _FORKED_REPOS:
            raise ValueError(f"bad repo URL: {url} [no fork exists]")

        return f'https://github.com/robust-rosin/{url_basename}'

    def repo(self, url: str) -> git.Repo:
        """Fetches the ROBUST fork of a given repository."""
        fork_url = self._repo_url_to_fork_url(url)
        repo_name = os.path.basename(url)
        repo_dir = os.path.join(self._forks_directory, repo_name)

        if os.path.exists(repo_dir):
            return git.Repo(repo_dir)
        else:
            return git.Repo.clone_from(fork_url, repo_dir)
