import Button from "../button/button.js";
import { formatFilesize, filetypeIcon } from "../format-util.js";
import { store } from "../upload/state.js";
import { setup } from "../setup.js";
const template = await setup('upload-file');

export default {
    components: {
        Button
    },
    data() {
        return {
            filetypeIcon,
            formatFilesize,
            store
        }
    },
    props: {
        name: String,
        size: String,
        type: String
    },
    template
}