#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict
import datetime
import os
import sys
import typing as t
import yamale
from yamale.schema import Schema
from yamale.validators import DefaultValidators, Validator
import yaml


# Script to validate either entire bug file or only sections of it



class Date(Validator):
    """ Custom Date validator """
    tag = 'date'

    def _is_valid(self, value):
        return isinstance(value, datetime.date)

validators = DefaultValidators.copy()
validators[Date.tag] = Date

dir_here = os.path.dirname(__file__)
schema_path = os.path.join(dir_here, 'robust.yaml')


class BugValidator:
    def __init__(self):
        self.yaml_ = self. _load(schema_path)

    # load yaml file - schema / bug
    def _load(self, filename: str) -> list:
        with open(filename, 'r') as f:
            return list(yaml.safe_load_all(f))[0]

    # create schema against which bug data will be validated
    def make_schema(self, *keys) -> None:
        if len(keys) == 0:  # create full schema
            self._schema = yamale.make_schema(schema_path, validators=validators)
            self._keys = None
            return

        self._keys = keys
        # create schema for specified keys
        kv = {k:v for k, v in self.yaml_.items() if k in keys}
        self._schema = yamale.make_schema(content=yaml.dump(kv), validators=validators)

    # add keys to an existing schema
    def add_include(self, key: str) -> None:
        kv = {key:self.yaml_[key]}
        self._schema.add_include(kv)

    def validate(self, bug_desc: t.Union[str, OrderedDict]) -> bool:
        if type(bug_desc) == str:
            bug_data = self._load(bug_desc)
        elif type(bug_desc) == OrderedDict:
            bug_data = bug_desc
        else:
            print(f"Unsupported data type for bug description")
            return False

        # validates only sections of bug for which the schema is created for
        if self._keys is None:
            data = yamale.make_data(bug_data)
        else:
            # print(f"validating bug description for sections {self._keys}")
            data_str = ''
            for key in self._keys:
                data_str += f"{key}: {bug_data[key]}\n"
            data = yamale.make_data(content=data_str)

        # Validate data against the schema. Throws a ValueError if data is invalid.
        try:
            yamale.validate(self._schema, data)
            # print('Validation success! 👍')
            return True
        except yamale.YamaleError as e:
            # print('Validation failed!\n')
            for result in e.results:
                # for error in result.errors:
                print(result.errors[0])

        return False


if __name__ == '__main__':
    validator = BugValidator()
    # validator.make_schema()   # creates schema for entire bug
    validator.make_schema('fault-codes', 'failure-codes')
    # validator.add_include('bug')
    # validator.validate(sys.argv[1])   # path for bug file
    data = OrderedDict([('id', '6e748c1'), ('title', 'Process Hanging in Shutdown Sequence'), ('description', 'ROS provides the concept of node (a process) and nodelet -- a lightweight implementation using a thread instead. Nodelets can be aggregated under a manager process, and this enables nodelets under the same manager to share messages by reference, avoiding the cost of copy and serialization. The Kobuki base nodelet spawns an additional thread for its operation: one thread publishes messages at a specific rate, and another processes event callbacks. When the user requested shutdown by killing both the manager and the nodelet, no problems arose. If the user tried to shutdown just the nodelet, then it would hang in the shutdown sequence. The reason behind this behaviour was that the nodelet manager would try to destroy the nodelet object, but the destructor waited for the additional thread to finish. However, no signal would be sent to the helper thread, and it would keep working indefinitely. The solution for this problem was to add a "shutdown requested" flag that would be shared between threads. When the manager tries to destroy the nodelet object, the destructor signals the other thread through the flag and only then proceeds to wait.\n'), ('classification', 'CWE-404: Improper Resource Shutdown or Release #RESOURCE'), ('keywords', ['concurrency', 'shutdown']), ('system', 'kobuki'), ('severity', 'error'), ('links', []), ('bug', OrderedDict([('phase', 'runtime'), ('specificity', 'general-issue'), ('architectural-location', 'application-specific code'), ('application', 'mobile robot'), ('task', None), ('subsystem', 'driver'), ('package', 'yujinrobot/kobuki/kobuki_node'), ('languages', ['C++']), ('detected-by', 'developer'), ('reported-by', 'member developer'), ('issue', 'https://github.com/yujinrobot/kobuki/issues/324'), ('time-reported', 1234), ('reproducibility', 'always'), ('trace', None)])), ('fix', OrderedDict([('pull-request', None), ('license', ['BSD']), ('fix-in', ['kobuki_node/src/nodelet/kobuki_nodelet.cpp']), ('languages', ['C++']), ('time', '2014-04-21 (07:38)'), ('commits', [OrderedDict([('repo', 'https://github.com/yujinrobot/kobuki'), ('hash', '6e748c1df1024847de91d899506ae872759d1094')])])])), ('fault-codes', ['CONCURRENCY:SIGNALS']), ('failure-codes', ['SOFTWARE:CONCURRENCY', 'SYSTEM:LIVENESS'])])

    validator.validate(data)
