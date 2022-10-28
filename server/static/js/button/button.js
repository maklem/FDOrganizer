import { setup } from "../setup.js";
const template = await setup('button');

export default {
    props: {
        type: String,
        disabled: Boolean,
        flat: Boolean
    },
    components: {
    },
    data() {
        return {
        }
    },
    methods: {
        /**
         * @param  {MouseEvent} event
         */
        buttonClicked(event) {
            !this.disabled && this.$emit('button-clicked');
        }
    },
    template
}