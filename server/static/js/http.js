
export async function put(url, body, headers) {
    return fetchWithType("PUT", url, body, headers)
}
export async function get(url, body, headers) {
    return fetchWithType("GET", url, body, headers)
}
export async function post(url, body, headers) {
    return fetchWithType("POST", url, body, headers)
}
export async function patch(url, body, headers) {
    return fetchWithType("PATCH", url, body, headers)
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
    let json = {}
    try {
        json = await response.json()
    } catch {
        if (response.status > 399) {
            throw new HTTPError(`${response.status} - ${response.statusText}`, response.status)
        } else {
            throw new Error("Received an invalid response from server. Please contact your administrator.")
        }
    }
    if (response.status > 399) throw new HTTPError(`${response.status} - ${json.message}`, response.status)
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

class HTTPError extends Error {
 constructor(message, status) {
  super(message)
  this.status = status
 }
}