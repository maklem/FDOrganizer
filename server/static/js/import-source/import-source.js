import { setup } from "../setup.js";
import Button from "../button/button.js"
import { getSessionToken, loginSource } from "../authentication.js";
import { get } from "../http.js"

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
            this.collections = await get(`import/${this.id}`);
        },
        selectCollection(collectionId) {
            this.collections = this.collections.map(collection => ({...collection, active: collection.id === collectionId}))
            this.$emit('select-project', collectionId)
        }
    },
    template
}