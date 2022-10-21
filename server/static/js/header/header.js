import { logout } from "../authentication.js";
import NavbarTab from "../navbar-tab/navbar-tab.js";
import { setup } from "../setup.js";
import TopBanner from "../top-banner/top-banner.js";

const template = await setup('header');

export default {
    components: {
        NavbarTab,
        TopBanner
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
        title: "Labfolder",
        url: "labfolder"
    },
    {
        title: "easyDB",
        url: "easydb"
    },
    {
        title: "Editor",
        url: "package"
    },
    {
        title: "Manual Upload",
        url: "upload"
    },
    {
        title: "Metadata",
        url: "metadata"
    },
    {
        title: "Archive",
        url: "lzv"
    },
    {
        title: "Review",
        url: "review"
    },

]