import { reactive } from '../vue.js';
import { validate } from '../validation-util.js';
import { put, get } from "../http.js"


export const store = reactive({
    modalRef: undefined,
    openImport,
    closeImport
});


function openImport(entityType, entityId, readonly = false) {
    store.modalRef.showModal()
}

function closeImport() {
    return store.modalRef.close()
}
