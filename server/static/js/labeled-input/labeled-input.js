import { setup } from "../setup.js";
import { localized } from "../format-util.js";
const template = await setup('labeled-input');

export default {
    components: {
    },
    props: {
        id: String,
        options: Array,
        label: String,
        placeholder: String,
        invalid: {
            type: Boolean,
            default: undefined
        },
        initialValue: String,
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