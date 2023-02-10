import {reactive} from '../vue.js';
import {store as editStore} from '../package-edit/state.js'

export const store = reactive({
    tabs: [],
    metadata: [],
    document: undefined,
    schema: undefined,
    subject: undefined,
    loading: {
        document: false,
    },
    getDocument,
});

async function getDocument(documentId) {
    const response = await fetch(`/document/${documentId}/metadata`)
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)

    store.document = json.document
    if (response.status === 200) store.metadata = json.metadata
}
