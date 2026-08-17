import { reactive } from '../vue.js';
import { store as metadatastore } from "../metadata/state.js";
import { validate } from '../validation-util.js';

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
        if(validate(data.data.id, "doi", false))
        {
            enshureList(metadatastore.metadata, "identifier")
            metadatastore.metadata.identifier.push({
                "resourceIdentifierDoi": [data.data.id],
                "resourceIdentifierScheme": ["doi"],
            });
            store.results.push(`Added Identifier DOI: ${data.data.id}`)
        } else {
            store.results.push(`Could not add Identifier "${data.data.id}" does not match DOI format.`)
        }
    }

    if(data.data.attributes)
    {
        if(data.data.attributes.creators)
        {
            enshureList(metadatastore.metadata, "creator")
            for(const creator_id in data.data.attributes.creators){
                const creator = data.data.attributes.creators[creator_id]

                if(creator.nameType == "Personal" && !!creator.givenName && !!creator.familyName)
                {
                    let affiType = "name"
                    let affiContentField = "creatorAffiliationName"
                    let affiContent = "FIXME"

                    console.log("affiliation", creator.affiliation)
                    if(creator.affiliation && creator.affiliation.length == 1){
                        const affi = creator.affiliation[0]
                        if(!!affi.name){
                            affiContent = affi.name
                        }

                        if(affi.affiliationIdentifierScheme == "ROR")
                        {
                            if(validate(affi.affiliationIdentifier, "ror", false)
                            ){
                                affiType = "ror"
                                affiContentField = "creatorAffiliationROR"
                                affiContent = affi.affiliationIdentifier
                            }
                        }
                    }

                    let newdata = {
                        "creatorType": [ "personal" ],
                        "personIdentifierType": [ "name" ],
                        "creatorFirstName": [ creator.givenName ],
                        "creatorLastName": [ creator.familyName ],
                        "creatorAffiliationIdentifierType": [ affiType ],
                    }
                    newdata[affiContentField] = [ affiContent ]

                    metadatastore.metadata.creator.push(newdata)

                    store.results.push(`Added creator "${creator.givenName} ${creator.familyName}", affiliated to "${affiType}: ${affiContent}"`)
                }
            }
        }
    }

    if(store.results.length > 0){
        metadatastore.touched = true
    }
    return true;
}

