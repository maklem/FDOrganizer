import {reactive} from '../vue.js';
import { store as toastStore } from "../toast/state.js"
import { validate } from '../validation-util.js';
import { put, get } from "../http.js"
import { CONTENT, RELATIONS, SCOPE, ORIGIN_AND_CREATION, USAGE_AND_RIGHTS } from './metadata-sections.js';


export const store = reactive({
    metadata: undefined,
    metadataId: undefined,
    touched: false,
    entity: undefined,
    entityType: undefined,
    schema: undefined,
    schemaVersion: "1",
    subject: undefined,
    loading: {
        entity: true,
    },
    modalRef: undefined,
    saveMetadata,
    checkConditions,
    getAllFields,
    makeTemplate,
    getParameterValue,
    reset,
    sectionLabel,
    openMetadata,
    closeDocument,
    checkMetadataParameters
});

async function getEntity(entityType, entityId) {
    store.loading.entity = true
    const json = await get(`/${entityType}/${entityId}/metadata`)

    store.entity = json[entityType]
    store.entityType = entityType

    if (!!json.metadata) {
        store.metadata = json.metadata.metadata
        store.schema = await getSchema(json.metadata.schema_version)
    }
    else {
        store.metadata = {}
        store.schema = await getSchema(store.schemaVersion)
    }
    store.loading.entity = false
}

function getParameterValue(entityType) {
    const params = new URLSearchParams(location.search);
    const entityId = params.get(entityType);
    // TODO: Throw more sensible error here
    if (!entityId) new Error(`No valid ${entityType}-ID as parameter value`)
    getEntity(entityType, entityId)
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
    await put(`/${store.entityType}/${store.entity.id}/metadata`, {
            metadata: filteredData,
            schema_version: store.schemaVersion,
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

function createSection(schema, fieldNames, label) {
    return schema.filter(field => fieldNames.includes(field.id))
}

function splitSchema(schema) {
    const required = createRequired(schema)
    return {
        required,
        content: createSection(schema, CONTENT, 'Content'),
        scope: createSection(schema, SCOPE, 'Data Scope'),
        provenance: createSection(schema, ORIGIN_AND_CREATION, 'Data Creation & Aquisition'),
        relations: createSection(schema, RELATIONS, 'Related Documents'),
        rights: createSection(schema, USAGE_AND_RIGHTS, 'Usage & Rights'),
    }
}

function sectionLabel(key) {
    if (!store.schema.hasOwnProperty(key)) return ''
    return LABELS[key]
}



function makeTemplate(field) {
    if (!!field.fields) 
        return field.fields.reduce((subfieldContainer,subfield) => {
            subfieldContainer[subfield.id] = makeTemplate(subfield)
            return subfieldContainer
        }, {})
    return [undefined]
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

        if (relation === "is") return fieldInstance[property]?.[0] === value
        if (relation === "exists") return fieldInstance[property] !== undefined && fieldInstance[property]?.[0] !== undefined
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


function reset() {
    store.metadata = undefined
    store.touched = false
    store.entity = undefined
    store.entityType = undefined
}

const LABELS = {
    required: 'Required',
    content: 'Content',
    relations: 'Related Documents',
    scope: 'Data Scope',
    provenance: 'Data Creation & Acquisition',
    rights: 'Usage & Rights'
}

function openMetadata(entityType, entityId) {
    history.pushState({[entityType]: entityId}, '', `?${entityType}=${entityId}`)
    addEventListener('popstate', function close() {
        store.closeDocument(entityType)
        removeEventListener('popstate', close)
    })
    store.getParameterValue(entityType)
    store.modalRef.showModal()
}

function closeDocument(entityType) {
    history.pushState({[entityType]: null}, '', `${location.origin}${location.pathname}`)
    store.reset()
    return store.modalRef.close()
}

function checkMetadataParameters() {
    const params = new URLSearchParams(location.search);
    const entityId = getParameter(params)
    if (!!entityId.length) store.openMetadata(entityId[0], entityId[1])
}

function getParameter(params) {
    if (!!params.get('document')) return ["document", params.get('document')]
    if (!!params.get('folder')) return ["folder", params.get('folder')]
    if (!!params.get('package')) return ["package", params.get('package')]
    return []
}

