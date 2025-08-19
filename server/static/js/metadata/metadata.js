import { setup } from "../setup.js";
import {store} from "./state.js";
import MetadataSection from "../metadata-section/metadata-section.js"
import Button from "../button/button.js"
import LabeledInput from "../labeled-input/labeled-input.js"
import Toast from "../toast/toast.js"
import VideoDialog from "../video-dialog/video-dialog.js"

const template = await setup('metadata');

export default {
    components: {
        MetadataSection,
        Button,
        LabeledInput,
        Toast,
        VideoDialog
    },
    props: {
    },
    data() {
        return {
            store,
            helpOverlay: true,
            JSON,
        }
    },
    computed: {
        iconClass() {
            switch (store.entityType) {
                case "document":
                    return "fa-file-lines"
                case "folder":
                    return "fa-folder"
                case "package":
                    return "fa-box"
                default:
                    return "fa-file-lines"
            }
        }
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