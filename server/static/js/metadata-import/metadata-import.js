import { setup } from "../setup.js";
import { store } from "./state.js";
import Button from "../button/button.js"
import LabeledInput from "../labeled-input/labeled-input.js"
import { store as metadatastore } from "../metadata/state.js"

const template = await setup('metadata-import');

export default {
    components: {
        Button,
        LabeledInput
    },
    props: {
    },
    data() {
        return {
            store,
            metadatastore,
            helpOverlay: true,
            JSON,
        }
    },
    computed: {
    },
    async mounted() {
        store.modalRef = this.$refs.modal
    },
    methods: {
        async save() {
            if (await this.store.saveMetadata()) this.store.closeDocument()
        }
    },
    template
}