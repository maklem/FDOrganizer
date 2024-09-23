import { setup } from "../setup.js";
import  Button  from '../button/button.js';
import { store } from '../package-edit/state.js'
import {formatFilesize, filetypeIcon} from '../format-util.js';

const template = await setup('package-content-document');

export default {
    props: {
        name: String,
        id: String,
        size: Number,
        source: String,
        type: String
    },
    components: {
        Button
    },
    data() {
        return {
            formatFilesize,
            filetypeIcon,
            store
        }
    },
    inject: ['editable'],
    methods: {
        openDialog() {
            this.$refs.documentDelete.showModal()
        },
        deleteDocument(id) {
            this.store.deleteDocument(id)
            this.$refs.documentDelete.close()
        }
    },
    template
}