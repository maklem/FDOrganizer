import {reactive} from '../vue.js';
import {get} from "../http.js"

export const store = reactive({
    has_errors: false,
    errors: [],
    check_package,
});

async function check_package(package_id) {
    const json = await get("/archive/check/"+package_id)
    if( json.status == "success" ){
        store.errors = [];
        store.has_errors = false;
    }else if( json.status == "error" ){
        store.errors = json.errors
        store.has_errors = true;
    }else{
        store.errors = ["Failed to communicate with storage backend.", "Please contact administrator."];
        store.has_errors = true;
    }
    console.log("For package ", package_id, "I found ", store.errors)
}
