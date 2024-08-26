import { setup } from "../setup.js";

const template = await setup('archive-settings-tab');

export default {
    props: {
        id: String,
        title: String,
        active: Boolean
    },
    template
}
