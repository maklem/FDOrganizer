import { setup } from "../setup.js";
import { localized } from "../format-util.js";
import { validate } from "../validation-util.js";
import { store } from "../metadata/state.js"
import LabeledInput from "../labeled-input/labeled-input.js"
import Button from "../button/button.js"
const template = await setup('metadata-field');

export default {
    name: "MetadataField",
    components: {
        LabeledInput,
        Button
    },
    props: {
        field: Object,
        path: Array
    },
    computed: {
        metadata() {
            return this.path.reduce((metadata, step) => {
                return metadata[step]
            }, store.metadata)[this.field.id] ?? []
        }
    },
    data() {
        return {
            localized,
            validate,
            store
        }
    },
    methods: {

        fullpath(index) {
            return [...this.path, this.field.id, index]
        },
        update(value, index){
            let metadata = this.store.metadata
            for (const step of this.path) {
                metadata = metadata[step]
            }
            if (metadata[this.field.id] === undefined) metadata[this.field.id] = value
            else metadata[this.field.id][index] = value
        },
        addField() {
            const dummy = this.store.makeTemplate(this.field)

            let metadata = this.store.metadata
            for (const step of this.path) {
                metadata = metadata[step]
            }

            if (Array.isArray(metadata[this.field.id])) metadata[this.field.id].push(!!this.field.fields ? dummy : dummy[0])
            else metadata[this.field.id] = !!this.field.fields ? [dummy] : dummy
        }
    },
    template
}