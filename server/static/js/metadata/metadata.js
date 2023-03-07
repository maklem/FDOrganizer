import { setup } from "../setup.js";
import {store} from "./state.js";
import MetadataSection from "../metadata-section/metadata-section.js"
import Button from "../button/button.js"
import LabeledInput from "../labeled-input/labeled-input.js"

const template = await setup('metadata');

export default {
    components: {
        MetadataSection,
        Button,
        LabeledInput
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
                if (!!documentId) {
                    this.store.getDocument(documentId)
                    this.$refs.modal.showModal()
                }
            }
        }
    },
    methods: {
    },
    template
}