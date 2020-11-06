var exports_;
var mappings;
var schemes;
var usersets;


var export_userset_mapping = {};
var userset_export_mapping = {};
var target_export = 'datacite_xml';
var scheme_identifier = userset['identifier']

function find_export() {
	var el = exports_.filter(ex=>ex.identifier == target_export);
	if (el.length > 0) {
		return el[0];
	}
}

function find_scheme() {
	var el = mappings.filter(ex=>ex.identifier == target_export);
	if (el.length > 0) {
		return el[0];
	}
}

function find_mapping() {
	var el = mappings.filter(ex=>ex.identifier_target_export == target_export && ex.identifier_source_schemes.includes(scheme_identifier));
	if (el.length > 0) {
		return el[0];
	}
}

function create_export_to_userset_identifier_dictionary(){
	for(var mapping_item in mapping.mappings){
		export_userset_mapping[mapping_item.target_entity] = mapping_item.source_entity;
		userset_export_mapping[mapping_item.source_entity] = mapping_item.target_entity;
 	}
}

function check_for_skip_if_empty(export_item, userset_location) {
	for (var ex_it in export_item.export_items) {
        if (ex_it.type == 'FIELD' && 'skip_if_empty' in ex_it && ex_it.skip_if_empty) {
            userset_related_fields = userset_location.fields.filter(x=>'field_identifier' in x && x.field_identifier == export_userset_mapping[ex_it.identifier]);
            if (userset_related_fields.length == 0) {
                return true;
            }
	}
    return false;
}

function remove_skip_if_empty_usersets(export_item, userset_locations){
    var output = [];
    for (var us_loc in userset_locations) {
        if (!check_for_skip_if_empty(export_item, us_loc)){
            output.push(us_loc)
        }
    }
    return output
}

function process_export_item(export_item,userset_location){
    var utput = '';
   	var userset_related_entitys = [];
    if (export_item.type == 'STRUCTURE'){
        if (check_for_skip_if_empty(export_item, userset_location)){
            return '';
        }
        if ('prefix' in export_item){
            output += export_item.prefix;
        }
        for (var ex_it in export_item.export_items){
            output += process_export_item(ex_it, userset_location);
        }
        if ('suffix' in export_item) {
            output += export_item.suffix;
        }
    }
    if (export_item.type == 'GROUP') {
        var export_identifier = export_item.identifier;
        var userset_related_entitys = userset_location.fields.filter(x=>'group_identifier' in x && x.group_identifier == export_userset_mapping.export_identifier);
        userset_related_entitys = remove_skip_if_empty_usersets(export_item, userset_related_entitys);
        if (userset_related_entitys.length > 0){
            if ('prefix' in export_item){
                output += export_item.prefix;
            }
            for (var us_it in userset_related_entitys) {
                if ('item_prefix' in export_item) {
                        output += export_item.item_prefix;
                }
                for (var ex_it in export_item.export_items) {
                    output += process_export_item(ex_it, us_it);
                }
                if ('item_suffix' in export_item) {
                        output += export_item.item_suffix;
                }
            }
            if ('suffix' in export_item) {
                output += export_item.suffix;
            }
        }
        else {
            if ('left_empty' in export_item) {
                output += export_item.left_empty;
            }
        }
    }
    if (export_item.type == 'FIELD'){
        var export_identifier = export_item.identifier;
        var userset_related_entitys = userset_location.fields.filter(x=>'field_identifier' in x && x.field_identifier == export_userset_mapping[export_identifier]);
        if (userset_related_entitys.length > 0){
            if ('prefix' in export_item){
                output += export_item.prefix;
            }
            for (var us_it in userset_related_entitys) {
                for (var val in us_it.values) {
                    if ('item_prefix' in export_item) {
                        output += export_item.item_prefix;
                    }
                    output += val;
                    if ('item_suffix' in export_item) {
                        output += export_item.item_suffix;
                    }
                }
            }
            if ('suffix' in export_item) {
                output += export_item.suffix;
            }
        }
        else:
            if ('left_empty' in export_item) {
                output += export_item.left_empty;
            }
    }
    return output;
}

function create_export(scheme,userset,export,mapping){
    var file_str = '';
    if (mapping['identifier_target_export'] != export['identifier'] || not userset['identifier'] in mapping['identifier_source_schemes']) {
        return 'error, identifiers not matching';
    }
    if ('file_prefix' in export) {
        file_str += export.file_prefix;
    }
    for (export_item in export.export_items) {
        file_str += process_export_item(export_item, userset);
    }
    if ('file_suffix' in export) {
        file_str += export.file_suffix;
    }
    console.log("Created Output:")
    console.log(file_str)
}