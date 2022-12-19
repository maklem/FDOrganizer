import { setup } from "../setup.js";
import Button from "../button/button.js"
import { getSessionToken, loginSource } from "../authentication.js";

const template = await setup('import-source');

export default {
    components: {
        Button
    },
    props: {
        id: String,
        name: String,
        active: Boolean,
        needsAuthentication: Boolean
    },
    data() {
        return {
            username: '',
            password: '',
            authenticated: false,
            collections: []
        }
    },
    watch: {
        authenticated(before, after) {
            before && this.getCollections()
        }
    },
    mounted() {
        const token = getSessionToken()[this.id];
        if (!!token) this.authenticated = true
    },
    methods: {
        authenticate(event) {
            event.preventDefault()
            loginSource(
                this.id,
                {
                    username: this.username,
                    password: this.password
                }
            ).then(() => this.authenticated = true)
        },
        setUsername(event) {
            this.username = event.currentTarget.value
        },
        setPassword(event) {
            this.password = event.currentTarget.value
        },
        async getCollections() {
            const response = await fetch(`import/${this.id}`);
            const collections = await response.json();
            this.collections = collections
        },
        selectCollection(collectionId) {
            this.collections = this.collections.map(collection => ({...collection, active: collection.id === collectionId}))
            this.$emit('select-project', collectionId)
        }
    },
    template
}