import { setup } from "../setup.js";
import { watchEffect } from "../vue.js";
import { store } from "./state.js";

const template = await setup('package-check');

export default {
    props: {
        package: String
    },
    computed: {
    },
    data() {
        return {
            store
        }
    },
    created() {
        console.log("PackageCheck: Created()");
    },
    mounted() {
        console.log("PackageCheck: Mounted()");
        this.$nextTick().then(() => {store.checkPackage(this.package)});
    },
    watchEffect() {
        console.log("PackageCheck: WatchEffect()");
        this.$nextTick().then(() => {store.checkPackage(this.package)});
    },
    template
}
