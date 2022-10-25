import { setup } from "../setup.js";
const template = await setup('button');

export default {
    props: {
        type: String,
        disabled: Boolean,
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
            event.stopPropagation()
            this.disabled && this.$emit('click');
        }
    },
    template
}