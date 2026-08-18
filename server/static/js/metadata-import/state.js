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


function _readAffiliation(affiliation) {
    let affiType = "name"
    let affiContentField = "creatorAffiliationName"
    let affiContent = "FIXME"

    console.log("affiliation", affiliation)
    if(!!affiliation && affiliation.length == 1){
        const affi = affiliation[0]
        if(!!affi.name){
            affiContent = affi.name
        }

        if(affi.affiliationIdentifierScheme == "ROR")
        {
            let identifier = affi.affiliationIdentifier
            if(identifier.substring(0,16) == "https://ror.org/")
            {
                identifier = identifier.substring(16)
            }
            if(validate(identifier, "ror", false)
            ){
                affiType = "ror"
                affiContentField = "creatorAffiliationROR"
                affiContent = identifier
            }
        }
    }
    return {
        "type": affiType,
        "field": affiContentField,
        "value": affiContent,
    }
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

    try{
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
                        const affi = _readAffiliation(creator.affiliation)

                        let newdata = {
                            "creatorType": [ "personal" ],
                            "personIdentifierType": [ "name" ],
                            "creatorFirstName": [ creator.givenName ],
                            "creatorLastName": [ creator.familyName ],
                            "creatorAffiliationIdentifierType": [ affi.type ],
                        }
                        newdata[affi.field] = [ affi.value ]

                        metadatastore.metadata.creator.push(newdata)

                        store.results.push(`Added creator "${creator.givenName} ${creator.familyName}", affiliated to "${affi.type}: ${affi.value}"`)
                    }
                }
            }
            if(data.data.attributes.titles)
            {
                enshureList(metadatastore.metadata, "title")

                for(const title_id in data.data.attributes.titles)
                {
                    const title = data.data.attributes.titles[title_id]

                    let type = "customTitle"
                    switch(title.titleType){
                        case undefined: type="mainTitle"; break
                        case 'Subtitle': type="subtitle"; break
                        case 'AlternativeTitle': type="alternativeTitle"; break
                        default: type="customTitle"; break
                    }

                    metadatastore.metadata.title.push({
                        "titleType": [ type ],
                        "titleText": [ title.title ]
                    })

                    store.results.push(`Added ${type} "${title.title}"`)
                }
            }
            if(data.data.attributes.descriptions)
            {
                enshureList(metadatastore.metadata, "description")
                for(const id in data.data.attributes.descriptions)
                {
                    const desc = data.data.attributes.descriptions[id]
                    let type=""
                    let field=""
                    switch(desc.descriptionType){
                        case "Abstract":
                            type = "descriptionAbstract"
                            field = "textAbstract"
                            break
                        case "TableOfContents":
                            type = "descriptionTOC"
                            field = "textTOC"
                            break
                        case undefined:
                        case "Methods":
                        case "SeriesInformation":
                        case "TechnicalInfo":
                        case "Other":
                        default:
                            type = "descriptionCustom"
                            field = "textCustom"
                    }
                    
                    let newdata = {
                        "descriptionType": [ type ],
                    }
                    newdata[field] = desc.description
                    metadatastore.metadata.description.push(newdata)

                    store.results.push(`Added description converting type ${desc.descriptionType} to ${type}`)
                }
            }
            if(data.data.attributes.subjects)
            {
                let DDC = []
                let GND = []
                let Wikidata = []

                for(const id in data.data.attributes.subjects)
                {
                    const subject = data.data.attributes.subjects[id]

                    if(!subject.classificationCode)
                    {
                        continue
                    }

                    if(subject.subjectScheme === "DDC"){
                        DDC.push(subject.classificationCode)
                    }
                    if(subject.subjectScheme === "Wikidata"){
                        Wikidata.push(subject.classificationCode)
                    }
                    if(subject.subjectScheme === "GND" && validate(subject.classificationCode, "gnd", false)){
                        GND.push(subject.classificationCode)
                    }
                }

                enshureList(metadatastore.metadata, "subject")

                if(DDC.length > 0){
                    metadatastore.metadata.subject.push({
                        "subjectIdentifierType": [ "ddc" ],
                        "subjectIdentifierDdc": DDC
                    })
                    store.results.push(`Added subject identifiers of type DDC`)
                }
                if(GND.length > 0){
                    metadatastore.metadata.subject.push({
                        "subjectIdentifierType": [ "gnd" ],
                        "subjectIdentifierGND": GND
                    })
                    store.results.push(`Added subject identifiers of type GND`)
                }
                if(Wikidata.length > 0){
                    metadatastore.metadata.subject.push({
                        "subjectIdentifierType": [ "wikidata" ],
                        "subjectIdentifierWikidata": Wikidata
                    })
                    store.results.push(`Added subject identifiers of type Wikidata`)
                }
            }
        }
    }
    catch(error)
    {
        console.error(error);
        store.error = error;
        return false;
    }
    
    if(store.results.length > 0){
        metadatastore.touched = true
    }
    return true;
}

