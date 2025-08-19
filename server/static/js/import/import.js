import ImportSource from "../import-source/import-source.js"
import ImportFile from "../import-file/import-file.js"
import Button from "../button/button.js"
import VideoDialog from "../video-dialog/video-dialog.js"
import {store} from './state.js'
import { setup } from "../setup.js";

const template = await setup('import');

export default {
    components: {
        ImportSource,
        ImportFile,
        Button,
        VideoDialog
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


