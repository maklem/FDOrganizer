import { logout } from "../authentication.js";
import NavbarTab from "../navbar-tab/navbar-tab.js";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";
import Button from "../button/button.js"

const template = await setup('header');

export default {
    components: {
        NavbarTab,
        TopBanner,
        Button
    },
    data() {
        return {
            tabs: tabs
        }
    },
    methods: {
        logout() {
            logout();
        }
    },
    template
}

const tabs = [
    {
        title: "Welcome",
        url: ""
    },
    {
        title: "Import",
        url: "import"
    },
    {
        title: "Editor",
        url: "package"
    },
    {
        title: "Archive",
        url: "lzv"
    },

]