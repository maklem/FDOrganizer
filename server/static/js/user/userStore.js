import {reactive} from '../vue.js';
import {get} from "../http.js"

export const userStore = reactive({
    name: "",
    displayname: "",
    organisation: "",
    reviewer: false,
    isLoading: false,
    loadUserInfo,
    copyToClipboard
});

async function loadUserInfo() {
    if(userStore.isLoading) return

    userStore.isLoading = true

    const json = await get("/whoami")
    userStore.name = json.name
    userStore.displayname = json.displayname
    userStore.organisation = json.organisation
    userStore.reviewer = json.reviewer
    userStore.plugins = json.plugins

    console.log(userStore)

    userStore.isLoading = false
}

function copyToClipboard() {
    const text = "Name: "+userStore.displayname+"\n"+
        "ID: "+userStore.name+"\n"+
        "ORG: "+userStore.organisation;
    navigator.clipboard.writeText(text);
}