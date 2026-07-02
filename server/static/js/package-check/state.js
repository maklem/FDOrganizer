import {reactive} from '../vue.js';
import {get} from "../http.js"

export const store = reactive({
    package: String,
    hasErrors: false,
    errors: [],
    checkPackage,
});

async function checkPackage(package_id) {
    if(package_id == store.package)
    {
        console.log("PackageCheck: Updating same id? Skipping.")
        return;
    }
    store.package = package_id;

    // resetting first
    store.errors = [];
    store.hasErrors = false;
    
    console.log("PackageCheck: updating ", package_id);
    const json = await get("/archive/check/"+package_id);

    if(store.package != package_id){
        console.log("PackageCheck: Racing Condition: package_id changed while waiting for response.")
        return;
    }

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
    console.log("PackageCheck: Updated data for package ", package_id);
}
