import { setup } from "../setup.js";
import { store } from "../metadata/state.js"
import MetadataField from "../metadata-field/metadata-field.js"


const template = await setup('metadata-section');

export default {
    components: {
        MetadataField
    },
    props: {
        id: String,
        label: String,
    },
    data() {
        return {
            store,
            open: false
        }
    },
    computed: {
        sectionId() {
            return this.id
        }
    },
    template
}