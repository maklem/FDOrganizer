import { getSessionToken, logout } from "../authentication.js";
import NavbarTab from "../navbar-tab/navbar-tab.js";
import NavbarWhoami from "../navbar-whoami/navbar-whoami.js";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";
import Button from "../button/button.js"

const template = await setup('header');

export default {
    components: {
        NavbarTab,
	NavbarWhoami,
        TopBanner,
        Button
    },
    computed: {
        tabs() {
           if (!getSessionToken().reviewer) return tabs.filter(tab => tab.url !== "review")
           return tabs
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
        url: "start"
    },
    {
        title: "Editor",
        url: "package"
    },
    {
        title: "Archive",
        url: "archive"
    },
    {
        title: "Review",
        url: "review"
    }

]
