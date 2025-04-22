import { setup } from "../setup.js";
const template = await setup('date-input');

export default {
    components: {
    },
    props: {
        id: String,
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
            asDate
        }
    },
    methods: {
        asTimestamp(event) {
            event.stopImmediatePropagation()
            const newValue = Date.parse(event.target.value)
            this.$emit('input', newValue)
        }
    },
    template
}

function asDate(value) {
    if (value === undefined) return ""
    if (isNaN(value)) return ""
    return new Date(parseInt(value)).toISOString().split('T')[0]
}