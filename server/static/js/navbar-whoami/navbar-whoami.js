import { setup } from "../setup.js";
import { userStore } from "../user/userStore.js";

const template = await setup('navbar-whoami');

export default {
    props: {
    },
    computed: {
    },
    data() {
        return {
            userStore
        }
    },
    mounted() {
        this.$nextTick().then(userStore.loadUserInfo);
    },
    template
}
