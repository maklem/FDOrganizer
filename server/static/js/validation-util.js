export function validate(content, type, ignoreEmpty = true) {
    if (content === "" || content === undefined) return ignoreEmpty ? true : false
    switch (type) {
        case "doi":
            return new RegExp('^10\\.\\d{4,9}\\/[\\-._;():A-Z0-9]+[\\-._;()\\/:A-Z0-9]*$', 'i').test(content)
        case "uri":
            return new RegExp('^(https?:\\/\\/)?(www\\.)?([\\w~-]{1,63}\\.)+?[a-z]{1,63}[\\w.~\\-\\/#]*$').test(content)
        case "orcid":
            return new RegExp('^(\\d{4}\\-){3}\\d{3}(\\d|X)$').test(content)
        case "letter-string":
            return new RegExp('^[a-z][a-z\\s]+[a-z]$', 'i').test(content)
        default:
            return true
    }
}