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
    props: {
        open: String
    },
    data() {
        return {
            store,
        }
    },
    watch: {
        open(now, before) {
            if (now === before) return
            if (before) {
                return this.$refs.modal.close()
            }
            if (now) {
                const params = new URLSearchParams(location.search);
                const packageId = params.get("package");
                if (!packageId) return
                this.$refs.modal.showModal()
            }
        }
    },
    methods: {
        async save() {
            if (await this.store.savePackageSettings()) this.$emit('close')
        }
    },
    template
}