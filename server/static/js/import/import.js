import ImportSource from "../import-source/import-source.js"
import ImportFile from "../import-file/import-file.js"
import {store} from './state.js'
import { setup } from "../setup.js";

const template = await setup('import');

export default {
    components: {
        ImportSource,
        ImportFile,
    },
    data() {
        return {
            store
        }
    },
    async mounted() {
        this.store.getSources()
    },
    template
}


