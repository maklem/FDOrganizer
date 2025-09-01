import { setup } from "../setup.js";
import Button from "../button/button.js"
import LabeledInput from "../labeled-input/labeled-input.js";
import ImportFile from "../import-file/import-file.js"
import { store } from "../import/state.js"
import { formatFilesize } from "../format-util.js";

const template = await setup('import-source');

export default {
    components: {
        Button,
        LabeledInput,
        ImportFile
    },
    props: {
        id: String,
        name: String,
        authenticated: Boolean,
        needsAuthentication: Boolean,
        authenticationType: String
    },
    data() {
        return {
            store,
            formatFilesize
        }
    },
    methods: {
        authenticate() {
            store.authenticate(this.id, this.authenticationType)
        }
    },
    template
}