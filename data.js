// data.js — Async loader for gzip-compressed resistor database
// The actual data is in resistors_compact.json.gz (~1-2 MB vs 9 MB uncompressed)
// Uses browser-native DecompressionStream API (Chrome 80+, Firefox 110+, Safari 16.4+)

const DATA_GZ_URL = 'resistors_compact.json.gz';

async function loadResistorData() {
    const resp = await fetch(DATA_GZ_URL);
    if (!resp.ok) throw new Error(`Failed to fetch ${DATA_GZ_URL}: ${resp.status}`);

    const blob = await resp.blob();
    const stream = blob.stream().pipeThrough(new DecompressionStream('gzip'));
    const reader = stream.getReader();
    const chunks = [];
    let totalLen = 0;

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        totalLen += value.length;
    }

    // Combine chunks into a single Uint8Array
    const allBytes = new Uint8Array(totalLen);
    let offset = 0;
    for (const chunk of chunks) {
        allBytes.set(chunk, offset);
        offset += chunk.length;
    }

    // Decode as UTF-8 and parse JSON
    const text = new TextDecoder('utf-8').decode(allBytes);
    return JSON.parse(text);
}
