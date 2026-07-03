import {reactive} from '../vue.js';
import {patch, get, put, dlt} from "../http.js"

export const store = reactive({
    title: String,
    type: String,
    messages: [],
    openDialog,
    closeDialog
});

function reset() {
    store.title = "Submitting..."
    store.type = "submitting"
    store.messages = []
}

function openDialog(title, type, messages) {
    store.title = title
    store.type = type
    store.messages = messages
    store.modalRef.showModal()
}

function closeDialog() {
    store.modalRef.close()
    reset()
}
