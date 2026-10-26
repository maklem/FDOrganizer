import { logout } from "../authentication.js";
import { userStore }  from "../user/userStore.js";
import NavbarTab from "../navbar-tab/navbar-tab.js";
import NavbarWhoami from "../navbar-whoami/navbar-whoami.js";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";
import Button from "../button/button.js"
import LocaleSwitch from "../locale-switch/locale-switch.js";

const template = await setup('header');

export default {
    components: {
        NavbarTab,
	    NavbarWhoami,
        TopBanner,
        Button,
        LocaleSwitch
    },
    data() {
        return {
            userStore
        }
    },
    computed: {
    },
    methods: {
        logout() {
            logout();
        }
    },
    template
}
