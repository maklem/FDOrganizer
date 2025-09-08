import { setup } from "../setup.js";
const template = await setup('number-input');

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
        value: String
    },
    data() {
        return {
            focus: false,
            step
        }
    },
    methods: {
        input(event) {
            event.stopImmediatePropagation()
            let newValue = sanitize(this.type, this.value, event.target.value)
            this.$emit('input', newValue)
        }
    },
    template
}

function sanitize(type, oldvalue, newvalue) {
    if (newvalue === "") return oldvalue
    if (type === "coordinate") return parseFloat(newvalue)
    if (type === "quantity") return parseInt(newvalue)
    return newvalue
}

function step(type) {
    if (type === "coordinate") return '.00000001'
    if (type === "quantity") return '1'
    return '1'
}