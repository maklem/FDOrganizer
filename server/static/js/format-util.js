/**
 * @param  {number} bytes
 */
export function formatFilesize(bytes) {
    return new Intl.NumberFormat('de-DE', {
        style: 'unit',
        maximumFractionDigits: 1,
        unit: getUnit(bytes)
    }).format(divide(bytes))
}
/**
 * @param  {number} bytes
 */
function getUnit(bytes) {
    if (bytes > 1000000000) return 'gigabyte';
    if (bytes > 1000000) return 'megabyte';
    if (bytes > 1000) return 'kilobyte';
    return 'byte';
}
/**
 * @param  {number} bytes
 */
function divide(bytes) {
    if (bytes > 1_000_000_000) return bytes / 1_000_000_000;
    if (bytes > 1_000_000) return bytes / 1_000_000;
    if (bytes > 1000) return bytes / 1_000;
    return bytes;
}
