import Button from "../button/button.js"
import { store } from "./state.js"
import { setup } from "../setup.js";
const template = await setup('status-dialog');

export default {
    components: {
        Button,
    },
    data() {
        return {
            store,
        }
    },
    async mounted() {
        store.modalRef = this.$refs.modal
    },
    methods: {
        openWaiting(title) {
            this.store.open(title, "submitting", [])
        },
        openError(title, messages) {
            this.store.open(title, "error", messages)
        },
        close() {
            this.store.close()
        },
    },
    template
}