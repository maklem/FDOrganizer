import { setup } from "../setup.js";
import {store} from "./state.js";


const template = await setup('metadata');

export default {
    components: {
    },
    props: {
        open: Boolean
    },
    data() {
        return {
            store
        }
    },
    watch: {
        open(now, before) {
            console.log('why')
            if (now === before) return
            if (before) {
                return this.$refs.modal.close()
            }
            if (now) {
                const params = new URLSearchParams(location.search);
                const documentId = params.get("document");
                if (!!documentId) {
                    this.store.getDocument(documentId)
                    this.$refs.modal.showModal()
                }
            }
        }
    },
    methods: {
    },
    template
}