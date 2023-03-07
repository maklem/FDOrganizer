import { setup } from "../setup.js";
import { store } from "../metadata/state.js"
import LabeledInput from "../labeled-input/labeled-input.js"
import Button from "../button/button.js"
import { localized } from "../format-util.js";
import { validate } from "../validation-util.js";

const template = await setup('metadata-section');

export default {
    components: {
        LabeledInput,
        Button,
    },
    props: {
        id: String,
        label: String,
    },
    data() {
        return {
            store,
            localized,
            validate,
            open: false
        }
    },
    computed: {
        sectionId() {
            return this.id
        }
    },
    watch: {
    },
    methods: {
        checkConditions(fieldInstance, subfield) {
            if (!subfield.conditions) return true
            return Object.keys(subfield.conditions).every(conditionKey => fieldInstance[conditionKey] === subfield.conditions[conditionKey])
        }
    },
    template
}