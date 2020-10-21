'''
test for metadata->mapping->export
'''
import json

with open('test_mapping.json') as f:
	mapping = json.loads(f)
with open('test_scheme.json') as f:
	scheme = json.loads(f)
with open('test_export.json') as f:
	export = json.loads(f)

