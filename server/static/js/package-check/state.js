import {reactive} from '../vue.js';
import {get} from "../http.js"

export const store = reactive({
    hasErrors: false,
    errors: [],
    checkPackage,
});

async function checkPackage(package_id) {
    console.log("Checking package ", package_id);
    const json = await get("/archive/check/"+package_id);
    if( json.status == "success" ){
        store.errors = [];
        store.hasErrors = false;
    }else if( json.status == "error" ){
        store.errors = json.details
        store.hasErrors = true;
    }else{
        store.errors = ["Failed to communicate with storage backend.", "Please contact administrator."];
        store.hasErrors = true;
    }
    console.log("For package ", package_id, "I found ", store.errors);
}
