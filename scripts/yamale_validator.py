# Import Yamale and make a schema object:
import sys
import os
import yamale
import datetime
from yamale.validators import DefaultValidators, Validator

class Date(Validator):
    """ Custom Date validator """
    tag = 'date'

    def _is_valid(self, value):
        return isinstance(value, datetime.date)

validators = DefaultValidators.copy()  # This is a dictionary
validators[Date.tag] = Date

dir_here = os.path.dirname(__file__)
schema_path = os.path.join(dir_here, 'robust.yaml')
data_path = os.path.join(dir_here, 'yamale.bug')

schema = yamale.make_schema(schema_path, validators=validators)

# Create a Data object
data = yamale.make_data(sys.argv[1])

# Validate data against the schema. Throws a ValueError if data is invalid.
try:
    yamale.validate(schema, data)
    print('Validation success! 👍')
except yamale.YamaleError as e:
    print('Validation failed!\n')
    for result in e.results:
        print("Error validating data '%s' with '%s'\n\t" % (result.data, result.schema))
        for error in result.errors:
            print('\t%s' % error)
    sys.exit(1)
