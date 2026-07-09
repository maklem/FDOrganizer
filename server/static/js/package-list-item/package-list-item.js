import { setup } from "../setup.js";
import { store } from "../package/state.js";
import Button from "../button/button.js";
import LabeledInput from "../labeled-input/labeled-input.js";
import { formatRelativeDate } from "../format-util.js";

const template = await setup('package-list-item');

export default {
    components: {
        Button,
        LabeledInput
    },
    props: {
        id: String,
        name: String,
        status: String,
        keep_until: String,
    },
    data() {
        return {
            store: store,
            newName: this.name,
            editMode: false,
            formatRelativeDate
        }
    },
    methods: {
        openDialog() {
            this.$refs.confirmDelete.showModal()
        },
        closeDialog() {
            this.$refs.confirmDelete.close()
        },
        deletePackage(id) {
            this.store.deletePackage(id)
            this.$refs.confirmDelete.close()
        }
    },
    template
}