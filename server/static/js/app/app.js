import Header from "../header/header.js";
import Toast from "../toast/toast.js";
import { setup } from "../setup.js";
import Footer from "../footer/footer.js";

const template = await setup('app');


export default {
    components: {
        Toast,
        Header,
        Footer
    },
    template
}
