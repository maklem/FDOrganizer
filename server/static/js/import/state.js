import {reactive} from '../vue.js';
import { get } from "../http.js"


export const store = reactive({
    files: [],
    selectedFiles: [],
    clearFiles: () => store.files = [],
    setFiles: (newFiles) => store.files = newFiles,
    toggleSelectFile,
    getFiles
});
/**
 * @param  {string} sourceId
 * @param  {string} collectionId
 * @returns {Promise<ImportFile[]>}
 */
async function getFiles(sourceId, collectionId) {
    store.files = await get(`import/${sourceId}/${collectionId}`)
}

function toggleSelectFile(fileId) {
    const fileToSelect = store.files.find(file => file.id === fileId)
    if (!fileToSelect) return

    if (store.selectedFiles.find(file => file.id === fileId)) 
        return store.selectedFiles = store.selectedFiles.filter(file => file.id !== fileId)
    
    store.selectedFiles.push(fileToSelect)
}
