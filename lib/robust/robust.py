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
    'rocon_app_platform',
    'cob_common',
    'rospkg',
    'rosdep',
    'openni_launch',
    'ecl_core',
    'rqt',
    'turtlebot_apps',
    'turtlebot_create',
    'gazebo_ros_pkgs',
    'cob_driver',
    'qt_gui_core',
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
class TotalCommitStats:
    insertions: int
    deletions: int
    lines: int
    files: int

    @staticmethod
    def from_dict(dict_: t.Mapping[str, int]) -> 'TotalCommitStats':
        return TotalCommitStats(insertions=dict_['insertions'],
                                deletions=dict_['deletions'],
                                lines=dict_['lines'],
                                files=dict_['files'])


@attr.s(auto_attribs=True, frozen=True, slots=True)
class FileCommitStats:
    filename: str
    insertions: int
    deletions: int
    lines: int

    @staticmethod
    def from_dict(filename: str,
                  dict_: t.Mapping[str, int]
                  ) -> 'FileCommitStats':
        return FileCommitStats(filename=filename,
                               insertions=dict_['insertions'],
                               deletions=dict_['deletions'],
                               lines=dict_['lines'])


@attr.s(auto_attribs=True, frozen=True, slots=True)
class CommitStats:
    total: TotalCommitStats
    files: t.AbstractSet[FileCommitStats]

    def __attrs_post_init__(self) -> None:
        object.__setattr__(self, 'files', frozenset(self.files))

    @staticmethod
    def from_dict(dict_: t.Mapping[str, t.Any]) -> 'CommitStats':
        def err(msg: str) -> t.NoReturn:
            raise ValueError(f'bad commit stats: {msg}')

        if 'total' not in dict_:
            err('missing "total" section')
        if 'files' not in dict_:
            err('missing "files" section')

        try:
            total = TotalCommitStats.from_dict(dict_['total'])
        except KeyError as error:
            err(f'missing "{error}" field in "total" section')

        files: t.Set[FileCommitStats] = set()
        for filename, file_dict in dict_['files'].items():
            try:
                file_stats = FileCommitStats.from_dict(filename, file_dict)
            except KeyError as error:
                err(f'missing "{error}" field in "files.{filename}" section')
            files.add(file_stats)

        return CommitStats(total, files)


@attr.s(auto_attribs=True, frozen=True, slots=True)
class FixCommit:
    repo: str
    hash_: str
    stats: t.Optional[CommitStats]


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
        filenames: t.List[str] = \
            self._read_field('fix-in', list, optional=True)
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

        # TODO handle corner cases: confidential, none, unknown
        commits_field = self._read_field('commits')
        if not isinstance(commits_field, list):
            raise ValueError("expected commits section to be a list")

        for commit_dict in commits_field:
            try:
                repo = commit_dict['repo']
                hash_ = commit_dict['hash']
            except KeyError as error:
                m = f"bad commit description: missing '{error}' property"
                raise ValueError(m) from error

            stats: t.Optional[CommitStats] = None
            if 'stats' in commit_dict:
                stats = CommitStats.from_dict(commit_dict['stats'])
            commit = FixCommit(repo, hash_, stats)
            commits.add(commit)

        return commits


@attr.s(auto_attribs=True, frozen=True, slots=True)
class FaultFailureSection:
    bug: 'BugDescription'

    def _get_value(self, key: str) -> t.Any:
        value: t.Any

        try:
            value = self.bug.yaml[key]
        except KeyError:
            message = (f"{self.bug.filename}: missing {key} "
                       "in bug description")
            print(message)

        return value

    @property
    def faults(self) -> t.Optional[t.List[str]]:
        return self._get_value('fault-codes')

    @property
    def failures(self) -> t.Optional[t.List[str]]:
        return self._get_value('failure-codes')


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
    def classification(self) -> str:
        return self.yaml['classification']

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

    @property
    def faults(self) -> t.Optional[t.List[str]]:
        return FaultFailureSection(self).faults

    @property
    def failures(self) -> t.Optional[t.List[str]]:
        return FaultFailureSection(self).faults

    def save(self) -> None:
        with open(self.filename, 'w') as f:
            yaml.dump(self.yaml, f)


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
