import { setup } from "../setup.js";
const template = await setup('upload-file');

export default {
    props: {
        name: String,
        size: String,
        icon: String,
        proxy: Boolean
    },
    template
}