import { reactive } from '../vue.js';
import { store as metadatastore } from "../metadata/state.js";

export const store = reactive({
    modalRef: undefined,
    modalResultsRef: undefined,
    error: "",
    results: [],
    openImport,
    closeImport,
    openResults,
    closeResults,
    mergeIntoMetadata
});


function openImport(entityType, entityId, readonly = false) {
    store.error = ""
    store.results = []
    store.modalRef.showModal()
}

function closeImport() {
    store.modalResultsRef.close()
    return store.modalRef.close()
}

function closeResults() {
    return store.modalResultsRef.close()
}

function openResults() {
    store.modalResultsRef.showModal()
}

function enshureList(object, name) {
    if(object.name === undefined){
        object.name = []
    }
    return object.name
}


function mergeIntoMetadata(inputtext) {
    console.log(`Received "${inputtext}" for parsing`);

    store.error = ""
    store.results = []
    
    let data = {}
    try {
        data = JSON.parse(inputtext);
    } catch(error) {
        console.error(error);
        store.error = error;
        return false;
    }

    if(!data.data){
        store.error = "Could not find metadata in JSON data. Tried to access property 'data' but it is not present."
        return false;
    }

    if(!!data.data.id){
        enshureList(metadatastore.metadata, "identifier")
        metadatastore.metadata.identifier.push({
            "resourceIdentifierDoi": [data.data.id],
            "resourceIdentifierScheme": ["doi"],
        });
        store.results.push(`Added Identifier DOI: ${data.data.id}`)
    }

    if(store.results.length > 0){
        metadatastore.touched = true
    }
    return true;
}

