# Import Yamale and make a schema object:
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

schema = yamale.make_schema('./robust.yaml', validators=validators)

# Create a Data object
data = yamale.make_data('./yamale.bug')

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
    exit(1)
