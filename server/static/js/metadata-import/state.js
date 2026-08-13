import { reactive } from '../vue.js';
import { store as metadatastore } from "../metadata/state.js";

export const store = reactive({
    modalRef: undefined,
    openImport,
    closeImport,
    mergeIntoMetadata
});


function openImport(entityType, entityId, readonly = false) {
    store.modalRef.showModal()
}

function closeImport() {
    return store.modalRef.close()
}

function mergeIntoMetadata(inputtext) {
    console.log(`Received "${inputtext}" for parsing`);
    const data = JSON.parse(inputtext);
    metadatastore.entity;
}