import { setup } from "../setup.js";
import { store } from "../archive/state.js";
import Button from "../button/button.js";
import { formatRelativeDate } from "../format-util.js";

const template = await setup('archive-list-item');

export default {
    components: {
        Button
    },
    props: {
        id: String,
        name: String,
        last_changed: String,
        keep_until: String,
        status: String
    },
    data() {
        return {
            store: store,
            formatRelativeDate
        }
    },
    template
}