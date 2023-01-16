import { setup } from "../setup.js";
import { store } from "../package/state.js";
import Button from "../button/button.js";

const template = await setup('package-list-item');

export default {
    components: {
        Button
    },
    props: {
        id: String,
        name: String,
        status: String
    },
    data() {
        return {
            store: store
        }
    },
    methods: {
        openDialog(event) {
            event.stopPropagation()
            this.$refs.confirmDelete.showModal()
        },
        closeDialog() {
            this.$refs.confirmDelete.close()
        },
    },
    template
}