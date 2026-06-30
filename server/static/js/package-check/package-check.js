import { setup } from "../setup.js";
import { store } from "./state.js";

const template = await setup('package-check');

export default {
    props: {
        package_id: String
    },
    computed: {
    },
    data() {
        return {
            store
        }
    },
    mounted() {
        this.$nextTick().then(store.check_package(package_id));
    },
    template
}
