import Button from "../button/button.js";
import { setup } from "../setup.js";
import { store } from "../import/state.js";
import {formatFilesize, filetypeIcon} from '../format-util.js';

const template = await setup('import-file');

export default {
    components: {
        Button
    },
    props: {
        id: String,
        name: String,
        size: Number,
        type: String,
        selected: Boolean
    },
    data() {
        return {
            filetypeIcon,
            formatFilesize,
            store
        }
    },
    template
}