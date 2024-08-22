import Button from "../button/button.js"
import LabeledInput from "../labeled-input/labeled-input.js"
import Toast from "../toast/toast.js"
import { store } from "./state.js"

import { setup } from "../setup.js";
const template = await setup('archive-package-settings');

export default {
    components: {
        Button,
        LabeledInput,
        Toast,
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
        async save() {
            if (await this.store.savePackageSettings()) this.store.closeSettings()
        }
    },
    template
}