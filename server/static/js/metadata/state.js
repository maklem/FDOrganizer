import {reactive} from '../vue.js';
import { store as toastStore } from "../toast/state.js"
import { validate } from '../validation-util.js';
import { put, get } from "../http.js"
import { CONTENT, RELATIONS, SCOPE, ORIGIN_AND_CREATION, USAGE_AND_RIGHTS } from './metadata-sections.js';
import { localized } from '../format-util.js';


export const store = reactive({
    metadata: undefined,
    metadataId: undefined,
    touched: false,
    document: undefined,
    schema: undefined,
    schemaVersion: "1",
    resourceType: {
        value: undefined,
        options: [],
    },
    subject: undefined,
    loading: {
        document: true,
    },
    getDocument,
    saveMetadata,
    addField,
    addSubfield,
    setResourceType,
    checkConditions,
    getAllFields,
    reset,
    sectionLabel
});

async function getDocument(documentId) {
    store.loading.document = true
    store.resourceType.options = RESOURCE_TYPES
    const json = await get(`/document/${documentId}/metadata`)

    store.document = json.document

    if (!!json.metadata) {
        store.metadata = json.metadata.metadata
        store.resourceType.value = json.metadata.resource_type
        store.schema = await getSchema(json.metadata.schema_version)
    }
    else {
        store.metadata = {}
        store.schema = await getSchema(store.schemaVersion)
    }
    store.loading.document = false
}

async function getSchema(version) {
    const json = await get(`/static/schema.json`)

    return splitSchema(json)
}

function getAllFields() {
    return Object.values(store.schema).reduce((schema, section) => [...schema, ...section], [])
}
async function saveMetadata() {
    const schema = store.getAllFields()
    const filteredData = filterUndefined(filterUnmetConditions(store.metadata, schema));

    if(!validateAll(filteredData, schema)) {
        toastStore.addMessage("error", "Manche Felder enthalten fehlerhafte Angaben")
        return false
    }
    await put(`/document/${store.document.id}/metadata`, {
            metadata: filteredData,
            schema_version: store.schemaVersion,
            resource_type: store.resourceType.value
        }
    )
    return true
}

function createRequired(schema) {
    const requiredFields = schema
    .filter(field => (field.min ?? 0) >= 1)

    requiredFields.forEach(field => {
        if(store.metadata[field.id] === undefined) store.metadata[field.id] = [makeTemplate(field)]
    })
    return requiredFields
}

function createResourceSpecific(schema) {
    return schema.filter(field => field.compatibleTypes?.includes(store.resourceType.value))
}

function createSection(schema, fieldNames, label) {
    return schema.filter(field => fieldNames.includes(field.id))
}

function splitSchema(schema) {
    const required = createRequired(schema)
    const resourceSpecific = createResourceSpecific(schema)
    return {
        required,
        content: createSection(schema, CONTENT, 'Content'),
        scope: createSection(schema, SCOPE, 'Data Scope'),
        provenance: createSection(schema, ORIGIN_AND_CREATION, 'Data Creation & Aquisition'),
        relations: createSection(schema, RELATIONS, 'Related Documents'),
        rights: createSection(schema, USAGE_AND_RIGHTS, 'Usage & Rights'),
        resourceSpecific,
    }
}

function sectionLabel(key) {
    if (!store.schema.hasOwnProperty(key)) return ''
    if (key === 'resourceSpecific') return resourceSectionLabel()
    return LABELS[key]
}

function resourceSectionLabel() {
    const resourceType = store.resourceType.options.find(type => type.id === store.resourceType.value)
    return `Specific for ${localized(resourceType.label)}` 
}
function addField(fieldId) {
    const field = store.getAllFields().find(field => field.id === fieldId)
    const dummy = makeTemplate(field)
    if (store.metadata?.[fieldId]?.length) store.metadata[fieldId].push(dummy)
    else store.metadata[fieldId] = [dummy]
}

function addSubfield(fieldId, index, subfieldId) {
    const field = store.getAllFields().find(field => field.id === fieldId).fields.find(subfield => subfield.id === subfieldId)
    const dummy = makeTemplate(field)
    if (store.metadata?.[fieldId][index][subfieldId]?.length) store.metadata[fieldId][index][subfieldId].push(dummy)
    else store.metadata[fieldId][index][subfieldId] = [dummy]
}

function makeTemplate(field) {
    if (!!field.fields) 
        return field.fields.reduce((subfieldContainer,subfield) => {
            subfieldContainer[subfield.id] = makeTemplate(subfield)
            return subfieldContainer
        }, {})
    return undefined
}

function filterUnmetConditions(data, schema) {
    if (schema === undefined) return data
    return Object.keys(data)
        .filter(key => {
            const subfield = schema.find(field => field.id === key)
            if (subfield === undefined) {
                console.warn(key, 'not found; ommiting value from metadata')
                return false
            }
            return checkConditions(data, schema.find(field => field.id === key))
        })
        .reduce((output, key) => {
            const schemaField = schema.find(field => field.id === key)
            if (!schemaField.fields) return {...output, [key]: data[key]}
            output[key] = data[key].map(fieldInstance => filterUnmetConditions(fieldInstance, schemaField.fields))
            return output
        }, {})
}

function filterUndefined(dataObject) {
    const newData = Object.entries(dataObject).reduce((filteredObject, [key, value]) => {

        if (value === undefined) return filteredObject
        if (Array.isArray(value)) {
            const filtered = value
            .map(singleValue => singleValue instanceof Object ? filterUndefined(singleValue) : singleValue)
            .filter(singleValue => !!singleValue)

            return filtered.length === 0 ? filteredObject : {...filteredObject, [key]: filtered}
        }
        else if (value instanceof Object) {
            const filtered = filterUndefined(value)
            return filtered === undefined ? filteredObject : {...filteredObject, [key]: filtered}
        }
        return {...filteredObject, [key]: value}
    }, {})
    return Object.keys(newData).length === 0 ? undefined : newData
}

function checkConditions(fieldInstance, subfield) {
    if (!subfield.conditions) return true
    
    return subfield.conditions.every(condition => {
        const property = condition[0]
        const relation = condition[1]
        const value = condition[2]

        if (relation === "is") return fieldInstance[property] === value
        if (relation === "exists") return fieldInstance[property] !== undefined
        console.warn(`Relation '${relation}' cannot be used to test condition on '${property}'`)
        return false
    })
}

function validateAll(metadata, schema) {
    return Object.entries(metadata).every(([key, value]) => {
        const field = schema.find(field => field.id === key)
        if(!!field.fields) return value.every(instance => validateAll(instance, field.fields))
        if(Array.isArray(value)) return value.every(instance => validate(instance, field.type, true))
        return validate(value, field.type, true)
    })
}

function setResourceType(value) {
    store.resourceType.value = value
}

function reset() {
    store.metadata = undefined
    store.touched = false
    store.document = undefined
    store.resourceType.value = undefined
}

const LABELS = {
    required: 'Required',
    content: 'Content',
    relations: 'Related Documents',
    scope: 'Data Scope',
    provenance: 'Data Creation & Acquisition',
    rights: 'Usage & Rights'
}

const RESOURCE_TYPES = [
    {
        "id": "audiovisual",
        "label": {
            "en": "Audiovisual",
            "de": "Audiovisuell"
        }
    },
    {
        "id": "book",
        "label": {
            "en": "Book",
            "de": "Buch"
        }
    },
    {
        "id": "bookChapter",
        "label": {
            "en": "Book chapter",
            "de": "Buchkapitel",
        } 
    },
    {
        "id": "collection",
        "label": {
            "en": "Collection",
            "de": "Sammlung"
        }
    },
    {
        "id": "computationalNotebook",
        "label": "Computational notebook"
    },
    {
        "id": "conferencePaper",
        "label": {
            "en": "Conference paper",
            "de": "Konferenzbeitrag",
        } 
    },
    {
        "id": "conferenceProceeding",
        "label": {
            "en": "Conference proceeding",
            "de": "Konferenzband",
        } 
    },
    {
        "id": "dataPaper",
        "label": {
            "en": "Data paper",
            "de": "Datenpublikation"
        }
    },
    {
        "id": "dataset",
        "label": {
            "en": "Dataset",
            "de": "Datenset"
        }
    },
    {
        "id": "dissertation",
        "label": "Dissertation"
    },
    {
        "id": "event",
        "label": {
            "en": "Event",
            "de": "Veranstaltung"
        }
    },
    {
        "id": "image",
        "label": {
            "en": "Image",
            "de": "Bild"
        }
    },
    {
        "id": "interactiveResource",
        "label": {
            "en": "Interactive resource",
            "de": "Interaktive Ressource"
        }
    },
    {
        "id": "journal",
        "label": {
            "en": "Journal",
            "de": "Zeitschrift",
        } 
    },
    {
        "id": "journalArticle",
        "label": {
            "en": "Journal article",
            "de": "Zeitschriftenartikel",
        } 
    },
    {
        "id": "model",
        "label": {
            "en": "Model",
            "de": "Modell"
        }
    },
    {
        "id": "outputManagementPlan",
        "label": {
            "en": "Output management plan",
            "de": "Output-Management Plan",
        } 
    },
    {
        "id": "peerReview",
        "label": {
            "en": "Peer review",
            "de": "Peer-review",
        } 
    },
    {
        "id": "physicalObject",
        "label": {
            "en": "Physical object",
            "de": "Physisches Medium"
        }
    },
    {
        "id": "preprint",
        "label": "Preprint"
    },
    {
        "id": "report",
        "label": "Report"
    },
    {
        "id": "service",
        "label": "Service",
    },
    {
        "id": "software",
        "label": "Software",
    },
    {
        "id": "sound",
        "label": {
            "en": "Sound",
            "de": "Audio"
        }
    },
    {
        "id": "standard",
        "label": "Standard"
    },
    {
        "id": "text",
        "label": "Text"
    },
    {
        "id": "workflow",
        "label": {
            "en": "Workflow",
            "de": "Prozessbeschreibung"
        }
    },
    {
        "id": "other",
        "label": {
            "en": "Other",
            "de": "Sonstige"
        }
    }
]