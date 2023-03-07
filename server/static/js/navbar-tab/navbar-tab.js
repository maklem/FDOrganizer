import { setup } from "../setup.js";

const template = await setup('navbar-tab');

export default {
    props: {
        url: String,
        title: String
    },
    computed: {
        isActive() {
            return window.location.pathname.startsWith('/' + this.url)
        }
    },
    template
}
