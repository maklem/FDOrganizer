import { createApp } from "../vue.js";
import App from "../app/app.js";
import ImportSource from "../import-source/import-source.js"
import ImportFile from "../import-file/import-file.js"
import Button from "../button/button.js";
import {store} from './state.js'
import { get } from "../http.js"
import { setup } from "../setup.js";

const template = await setup('import');

createApp({
    components: {
        App,
        ImportSource,
        ImportFile,
        Button
    },
    data() {
        return {
            sources: [],
        }
    },
    computed: {
        selectedFiles() {
            return store.selectedFiles
        },
        activeSource() {
            return this.sources.find(source => source.active)
        },
        formattedFiles() {
            return store.files.map(file => ({
                ...file,
                selected: store.selectedFiles.map(selectedFile => selectedFile.id).includes(file.id),
                name: file.displayname,
            }))
        }
    },
    async mounted() {
        const sources = await getSources()
        this.sources = sources.map(source => ({...source, active: false}))
    },
    methods: {
        
        /**
         * @param  {string} sourceId
         */
        activate(sourceId) {
            store.clearFiles();
            this.sources = this.sources
            .map(source => ({...source, active: source.id === sourceId}))
        },
        async showFiles(sourceId, collectionId) {
            store.clearFiles();
            await store.getFiles(sourceId, collectionId);
        },
        toggleSelectFile(fileId) {
            store.toggleSelectFile(fileId)
        }
    },
    template
}).mount('#app-container')
/**
 * @returns {Promise<Source[]>}
 */
async function getSources() {
    return await get('import/sources')
}

