import { setup } from "../setup.js";
import  Button  from '../button/button.js'
import {formatFilesize, filetypeIcon} from '../format-util.js';
import { store } from '../package-edit/state.js';

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
        openDialog(event) {
            event.stopPropagation()
            this.$refs.documentDelete.showModal()
        }
    },
    template
}