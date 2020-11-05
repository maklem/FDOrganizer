'''
test for metadata->mapping->export
'''
import json

with open('test_mapping.json') as f:
    mappings = json.load(f)
with open('metaDataSchemes.json') as f:
    schemes = json.load(f)
with open('test_export.json') as f:
    exports = json.load(f)
with open('test_meta_userset.json') as f:
    userset = json.load(f)

target_export = 'datacite_xml'
scheme_identifier = userset['identifier']
export_userset_mapping = {}
userset_export_mapping = {}

def find_export():
    el = [x for x in exports if x['identifier'] == target_export]
    if el:
        return el[0]

def find_scheme():
    el = [x for x in schemes if x['identifier'] == scheme_identifier]
    if el:
        return el[0]

def find_mapping():
    el = [x for x in mappings if x['identifier_target_export'] == target_export\
                                and scheme_identifier in x['identifier_source_schemes']]
    if el:
        return el[0]

def create_export(scheme,userset,export,mapping):
    file_str = ''
    if mapping['identifier_target_export'] != export['identifier'] or not userset['identifier'] in mapping['identifier_source_schemes']:
        return 'error, identifiers not matching'
    if 'file_prefix' in export:
        file_str += export['file_prefix']
    for export_item in export['export_items']:
        file_str += process_export_item(export_item, userset)
    if 'file_suffix' in export:
        file_str += export['file_suffix']
    print("Created Output:")
    print(file_str)


def process_export_item(export_item,userset_location):
    output = ''
    userset_related_entitys = []
    if export_item['type'] == 'STRUCTURE':
        print(json.dumps(export_item))
        print(json.dumps(userset_location))
        if check_for_skip_if_empty(export_item, userset_location):
            return ''
        if 'prefix' in export_item:
            output += export_item['prefix']
        for ex_it in export_item['export_items']:
            output += process_export_item(ex_it, userset_location)
        if 'suffix' in export_item:
            output += export_item['suffix']
    if export_item['type'] == 'GROUP':
        export_identifier = export_item['identifier']
        # print("processing group:")
        # print("export item:")
        # print(json.dumps(export_item))
        # print("userset_location:")
        # print(json.dumps(userset_location['fields']))
        # print("export_userset_mapping[export_identifier]")
        # print(export_userset_mapping[export_identifier])
        userset_related_entitys = [x for x in userset_location['fields']\
                                   if 'group_identifier' in x and x['group_identifier'] == export_userset_mapping[export_identifier]]
        userset_related_entitys = remove_skip_if_empty_usersets(export_item, userset_related_entitys)
        if userset_related_entitys:
            if 'prefix' in export_item:
                output += export_item['prefix']
            for us_it in userset_related_entitys:
                if 'item_prefix' in export_item:
                        output += export_item['item_prefix']
                for ex_it in export_item['export_items']:
                    output += process_export_item(ex_it, us_it)
                if 'item_suffix' in export_item:
                        output += export_item['item_suffix']
            if 'suffix' in export_item:
                output += export_item['suffix']
        else:
            if 'left_empty' in export_item:
                output += export_item['left_empty']
    if export_item['type'] == 'FIELD':
        export_identifier = export_item['identifier']
        userset_related_entitys = [x for x in userset_location['fields'] if 'field_identifier' in x and x['field_identifier'] == export_userset_mapping[export_identifier]]
        if userset_related_entitys:
            if 'prefix' in export_item:
                output += export_item['prefix']
            for us_it in userset_related_entitys: #this should only be one, but you never know ;)
                for val in us_it['values']:
                    if 'item_prefix' in export_item:
                        output += export_item['item_prefix']
                    output += val
                    if 'item_suffix' in export_item:
                        output += export_item['item_suffix']
            if 'suffix' in export_item:
                output += export_item['suffix']
        else:
            if 'left_empty' in export_item:
                output += export_item['left_empty']
    return output

def remove_skip_if_empty_usersets(export_item, userset_locations):
    output = []
    for us_loc in userset_locations:
        if not check_for_skip_if_empty(export_item, us_loc):
            output.append(us_loc)
    return output

def check_for_skip_if_empty(export_item, userset_location):
    for ex_it in export_item['export_items']:
        if ex_it['type'] == 'FIELD' and 'skip_if_empty' in ex_it and ex_it['skip_if_empty']:
            print('ex_it')
            print(json.dumps(ex_it))
            print(json.dumps(userset_location))
            userset_related_fields = [x for x in userset_location['fields'] if 'field_identifier' in x and x['field_identifier'] == export_userset_mapping[ex_it['identifier']]]
            print(userset_related_fields)
            if not userset_related_fields:
                return True
    return False

def create_export_to_userset_identifier_dictionary():
    for mapping_item in mapping['mappings']:
        export_userset_mapping[mapping_item['target_entity']] = mapping_item['source_entity']
        userset_export_mapping[mapping_item['source_entity']] = mapping_item['target_entity'] 


def resolve_export_identifier_to_scheme_identifier(export_identifier):
    return export_userset_mapping[export_identifier]

#checks if the group/structure has content in userset. uses mapping to find the releated fields
#when coming from a flat metadata structure, we dont have related group fields, so we only check
#if there exists a field which related to content in this group/structure
def check_if_export_group_has_mapped_field_content_in_userset(group):
    for item in group.export_items:
        if item.type == 'FIELD':
            val = check_userset_for_related_fields(item.identifier,item.type)
            if val:
                return True
        else:
            val = check_if_export_group_has_mapped_field_content_in_userset(item)
            if val:
                return True
    return False        


#checks if the userset has an instance of the field defined by mapping and the export_identifer
# export_identifier == mapping.target_entity -> mapping.source_entity == userset.field|group.identifier
def check_userset_for_related_fields(export_identifier, entity_type):
    schema_identifier = export_userset_mapping[export_identifier]
    return recursive_check_for_fields(userset, schema_identifier, entity_type)


def recursive_check_for_fields(obj, identifier, entity_type):
    for field in obj.fields:
        if hasattr(field, 'group_identifier'): #field is a group
            if entity_type == 'GROUP' and identifer == field.group_identifier:
                return True
            for gr_field in field.fields:
                val = recursive_check_for_fields(gr_field, identifier, entity_type)
                if val:
                    return True
        else: #field is a field
            if entity_type == 'FIELD' and identifier == field.field_identifier:
                return True
    return False            


if __name__ == "__main__":
    mapping = find_mapping()
    export = find_export()
    scheme = find_scheme()
    create_export_to_userset_identifier_dictionary()
    create_export(scheme, userset, export, mapping)