import { setup } from "../setup.js";
const template = await setup('default-input');

export default {
    components: {
    },
    props: {
        id: String,
        type: String,
        invalid: {
            type: Boolean,
            default: undefined
        },
        disabled: {
            type: Boolean,
            default: false
        },
        value: String,
        type: String
    },
    data() {
        return {
            focus: false,
        }
    },
    methods: {
        input(event) {
            event.stopImmediatePropagation()
            this.$emit('input', event.target.value)
        }
    },
    template
}