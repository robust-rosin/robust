# Import Yamale and make a schema object:
import yamale
schema = yamale.make_schema('./robust.yaml')

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