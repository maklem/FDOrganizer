import {reactive} from '../vue.js';
import {get} from "../http.js"

export const store = reactive({
    name: "",
    displayname: "",
    organisation: "",
    loadUserInfo,
});

async function loadUserInfo() {
    const json = await get("/whoami")
    store.name = json.name
    store.displayname = json.displayname
    store.organisation = json.organisation
    console.log("I am ", json.displayname)
}
