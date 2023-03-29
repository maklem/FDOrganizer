import { setup } from "../setup.js";
import {store} from "./state.js";
import MetadataSection from "../metadata-section/metadata-section.js"
import Button from "../button/button.js"
import LabeledInput from "../labeled-input/labeled-input.js"
import Toast from "../toast/toast.js"

const template = await setup('metadata');

export default {
    components: {
        MetadataSection,
        Button,
        LabeledInput,
        Toast
    },
    props: {
        open: String
    },
    data() {
        return {
            store,
            helpOverlay: true,
            JSON,
        }
    },
    watch: {
        open(now, before) {
            if (now === before) return
            if (before) {
                store.reset()
                return this.$refs.modal.close()
            }
            if (now) {
                const params = new URLSearchParams(location.search);
                const documentId = params.get("document");
                if (!documentId) return
                this.store.getDocument(documentId)
                this.$refs.modal.showModal()
            }
        }
    },
    methods: {
        async save() {
            if (await this.store.saveMetadata()) this.$emit('close')
        }
    },
    template
}