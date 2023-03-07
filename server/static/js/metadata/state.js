import {reactive} from '../vue.js';

export const store = reactive({
    metadata: undefined,
    metadataId: undefined,
    touched: false,
    document: undefined,
    schema: {
        required: undefined,
        content: undefined,
        relations: undefined,
        // timeAndPlace: undefined,
        // usageAndRights: undefined,
        // resourceSpecific: undefined
    },
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
    reset
});

async function getDocument(documentId) {
    store.loading.document = true
    store.resourceType.options = RESOURCE_TYPES
    const response = await fetch(`/document/${documentId}/metadata`)
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)

    store.document = json.document

    if (response.status !== 206) {
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
    const response = await fetch(`/static/schema.json`)
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)

    return splitSchema(json)
}

async function saveMetadata() {
    const schema = Object.values(store.schema).reduce((schema, section) => [...schema, ...section], [])
    const filteredData = filterUndefined(filterUnmetConditions(store.metadata, schema));

    const response = await fetch(`/document/${store.document.id}/metadata`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            metadata: filteredData,
            schema_version: store.schemaVersion,
            resource_type: store.resourceType.value
        })
    })
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
}

function createRequired(schema) {
    const requiredFields = schema
    .filter(field => (field.min ?? 0) >= 1)

    requiredFields.forEach(field => {
        if(store.metadata[field.id] === undefined) store.metadata[field.id] = [makeTemplate(field)]
    })
    return requiredFields
}

function createContent(schema) {
    const contentFields = ['subject', 'description']
    return schema.filter(field => contentFields.includes(field.id))
}


function createRelations(schema) {
    return schema.filter(field => field.id === 'relation')
}

function splitSchema(schema) {
    return {
        required: createRequired(schema),
        content: createContent(schema),
        relations: createRelations(schema),
    }
}

function addField(id, fieldId) {
    const field = store.schema[id].find(field => field.id === fieldId)
    const dummy = makeTemplate(field)
    if (store.metadata?.[fieldId]?.length) store.metadata[fieldId].push(dummy)
    else store.metadata[fieldId] = [dummy]
}

function addSubfield(id, fieldId, index, subfieldId) {
    const field = store.schema[id].find(field => field.id === fieldId).fields.find(subfield => subfield.id === subfieldId)
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
                console.log(key, 'not found; ommiting value')
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
    return Object.keys(subfield.conditions).every(conditionKey => fieldInstance[conditionKey] === subfield.conditions[conditionKey])
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

const RESOURCE_TYPES = [
    {
        "id": "audiovisual",
        "label": {
            "en": "Audiovisual",
            "de": "Audiovisuell"
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
        "id": "dataPaper",
        "label": {
            "en": "Data Paper",
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
            "en": "Interactive Resource",
            "de": "Interaktive Ressource"
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
        "id": "physicalObject",
        "label": {
            "en": "Physical Object",
            "de": "Physisches Medium"
        }
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
            "de": "Anderes"
        }
    }
]