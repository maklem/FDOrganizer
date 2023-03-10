
export async function put(url, body, headers) {
    return fetchWithType("PUT", url, body, headers)
}
export async function get(url, body, headers) {
    return fetchWithType("GET", url, body, headers)
}
export async function post(url, body, headers) {
    return fetchWithType("POST", url, body, headers)
}
export async function dlt(url, body, headers) {
    return fetchWithType("DELETE", url, body, headers)
}

async function fetchWithType(type, url, httpBody, new_headers) {
    const bodyAllowed = ['DELETE', 'POST', "PUT", "PATCH"].includes(type)

    const headers = setHeaders(new_headers)

    let body = undefined
    if (bodyAllowed && httpBody !== undefined) body = transformBodyForType(httpBody, headers["Content-Type"])

    const options = {
        headers,
        method: type,
        body
    }

    const response = await fetch(url, options);
    const json = await response.json()
    if (response.status > 399) throw new Error(`${response.status} - ${json.message}`)
    return json
}

function transformBodyForType(body, contentType) {
    switch (contentType) {
        case "application/json":
            return JSON.stringify(body)
        default:
            return body
    }
}

function setHeaders(provided) {
    const defaultHeaders = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if(!!provided) {
        const headers = {
            ...defaultHeaders,
            ...provided
        }
        if(headers["Content-Type"] === "multipart/form-data") delete headers["Content-Type"]
        return headers
    }
    return defaultHeaders  
}