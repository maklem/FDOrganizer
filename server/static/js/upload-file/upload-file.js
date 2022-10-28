import Button from "../button/button.js";
import { setup } from "../setup.js";
const template = await setup('upload-file');

export default {
    components: {
        Button
    },
    props: {
        name: String,
        size: String,
        icon: String,
        proxy: Boolean
    },
    template
}