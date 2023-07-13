import { setup } from "../setup.js";
import { localized } from "../format-util.js";
import DateInput from "../date-input/date-input.js";
import DefaultInput from "../default-input/default-input.js";
import NumberInput from "../number-input/number-input.js";
import TextareaInput from "../textarea-input/textarea-input.js";
const template = await setup('labeled-input');

export default {
    components: {
        DateInput,
        DefaultInput,
        NumberInput,
        TextareaInput
    },
    props: {
        id: String,
        options: Array,
        label: String,
        type: String,
        placeholder: String,
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
        }
    },
    computed: {
        opts() {
            return !this.value ? [...this.options, {id: undefined, label: "---"}] : this.options
        }
    },
    computed: {
        localizedLabel() {
            return localized(this.label)
        },
        localizedOptions() {
            const opts = this.options.map(option => ({...option, label: localized(option.label)}))
            return !this.value ? [...opts, {id: undefined, label: "---"}] : opts
        },
    },
    methods: {
        select(event) {
            event.stopPropagation()
            const newValue = event.target.value
            if(!this.options) this.$emit('input', newValue)
            else {
                const option = this.options.find(option => option.id === newValue)
                this.$emit('input', option?.id ?? newValue)
            }
        }
    },
    template
}