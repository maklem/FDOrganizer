class metadata_export_handler {
    //creates an export handler for a combination of export & mapping. can then be called with individual usersets to get exports

    constructor(export_definition,mapping) {
        if (mapping['identifier_target_export'] != export_definition['identifier']) {
            throw 'error, identifiers from mapping and export dont fit.';
        }
        this.export_definition = export_definition;
        this.mapping = mapping;
        this.export_userset_mapping = {};
        // this.userset_export_mapping = {};
        this.create_export_to_userset_identifier_dictionary(mapping);
}

    create_export_to_userset_identifier_dictionary(mapping){
	for(var mapping_item of mapping.mappings){
		this.export_userset_mapping[mapping_item.target_entity] = mapping_item.source_entity;
		// this.userset_export_mapping[mapping_item.source_entity] = mapping_item.target_entity;
 	}
}

    check_for_skip_if_empty(export_item, userset_location) {
	for (var ex_it of export_item.export_items) {
        if (ex_it.type == 'FIELD' && 'skip_if_empty' in ex_it && ex_it.skip_if_empty) {
            var userset_related_fields = userset_location.fields.filter(x=>'field_identifier' in x && x.field_identifier == this.export_userset_mapping[ex_it.identifier]);
            if (userset_related_fields.length == 0) {
                return true;
            }
        }
	}
    return false;
}

    remove_skip_if_empty_usersets(export_item, userset_locations){
    var output = [];
    for (var us_loc of userset_locations) {
        if (!this.check_for_skip_if_empty(export_item, us_loc)){
            output.push(us_loc);
        }
    }
    return output;
}

    process_export_item(export_item,userset_location){
    var output = '';
   	// var userset_related_entitys = [];
    if (export_item.type == 'STRUCTURE'){
        if (this.check_for_skip_if_empty(export_item, userset_location)){
            return '';
        }
        if ('prefix' in export_item){
            output += export_item.prefix;
        }
        for (var ex_it of export_item.export_items){
            output += this.process_export_item(ex_it, userset_location);
        }
        if ('suffix' in export_item) {
            output += export_item.suffix;
        }
    }
    if (export_item.type == 'GROUP') {
        var export_identifier = export_item.identifier;
        console.log(export_identifier);
        var userset_related_entitys = userset_location.fields.filter(x=>'group_identifier' in x && x.group_identifier == this.export_userset_mapping[export_identifier]);
        console.log(JSON.stringify(userset_related_entitys));
        userset_related_entitys = this.remove_skip_if_empty_usersets(export_item, userset_related_entitys);
        console.log(JSON.stringify(userset_related_entitys));
        if (userset_related_entitys.length > 0){
            if ('prefix' in export_item){
                output += export_item.prefix;
            }
            for (var us_it of userset_related_entitys) {
                if ('item_prefix' in export_item) {
                        output += export_item.item_prefix;
                }
                for (var ex_it of export_item.export_items) {
                    output += this.process_export_item(ex_it, us_it);
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
        var userset_related_entitys = userset_location.fields.filter(x=>'field_identifier' in x && x.field_identifier == this.export_userset_mapping[export_identifier]);
        if (userset_related_entitys.length > 0){
            if ('prefix' in export_item){
                output += export_item.prefix;
            }
            for (var us_it of userset_related_entitys) {
                for (var val of us_it.values) {
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
        else {
            if ('left_empty' in export_item) {
                output += export_item.left_empty;
            }
        }
    }
    return output;
}


//Entry Function for export functionality
    create_export(userset){
    var file_str = '';
    if (!userset['identifier'] in this.mapping['identifier_source_schemes'] ) {
        throw 'error, identifier of provided userset does not match with source_identifier in mapping';
    }
    if ('file_prefix' in this.export_definition) {
        file_str += this.export_definition.file_prefix;
    }
    for (var export_item of this.export_definition.export_items) {
        file_str += this.process_export_item(export_item, userset);
    }
    if ('file_suffix' in this.export_definition) {
        file_str += this.export_definition.file_suffix;
    }
    return file_str;
}

}