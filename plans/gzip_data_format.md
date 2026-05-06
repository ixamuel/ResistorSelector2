# Gzip Data Format — Analysis

## The Idea

Instead of serving `data.js` as raw JavaScript (9 MB), serve it as a **compressed `.json.gz`** file that the browser fetches and decompresses in JavaScript.

## How It Would Work

### Pipeline change:
```
extract_from_xlsm.py
  → resistors_compact.json  (7.3 MB)
  → resistors_compact.json.gz  (~1-2 MB)  ← NEW
  → data.js  (just a fetch + decompress wrapper, ~1 KB)
```

### Frontend change (`data.js`):
```js
// data.js — now just a tiny loader
async function loadData() {
  const resp = await fetch('resistors_compact.json.gz');
  const blob = await resp.blob();
  const ds = new DecompressionStream('gzip');
  const decompressed = blob.stream().pipeThrough(ds);
  const reader = decompressed.getReader();
  // ... accumulate chunks, parse JSON
  const DATA = JSON.parse(decodedText);
  // Then proceed with init()
}
```

## Estimated Size Comparison

| Format | Size | Savings |
|--------|------|---------|
| Current `data.js` (uncompressed) | ~9.0 MB | — |
| `resistors_compact.json.gz` | **~1.0-1.5 MB** | **~83-89%** |
| `data.js` (loader wrapper) | ~1 KB | — |

## Pros

- **Huge size reduction** — gzip typically achieves 70-85% compression on JSON
- **Minimal code changes** — only `data.js` and the pipeline need updating
- **No server config needed** — works with any static file host
- **No frontend logic changes** — the data structure stays exactly the same
- **Progressive enhancement** — the app still works, just loads faster

## Cons

- **Requires `DecompressionStream` API** — supported in all modern browsers (Chrome 80+, Firefox 110+, Safari 16.4+, Edge 80+), but NOT in older browsers
- **Async loading** — the app becomes async; need to handle loading state
- **Slightly more complex init** — can't just use `<script src="data.js">` anymore

## Browser Support Check

`DecompressionStream` is available in:
- Chrome 80+ (2020) ✅
- Edge 80+ (2020) ✅
- Firefox 110+ (2023) ✅
- Safari 16.4+ (2023) ✅
- **No IE11 support** (but that's expected for modern apps)

## Alternative: Fetch + ArrayBuffer + pako.js (for older browser support)

If you need to support older browsers, use the [`pako`](https://github.com/nodeca/pako) library (1.5 KB gzipped) as a fallback:
```js
// Load pako from CDN as fallback
if (!window.DecompressionStream) {
  // Use pako.inflate() instead
}
```

## Recommendation

**Yes, this is an excellent approach.** It's simple, effective, and requires minimal changes:

1. **Pipeline change:** Add gzip compression step after generating `resistors_compact.json`
2. **`data.js` change:** Replace the static data with a fetch + decompress loader
3. **`index.html` change:** Add a loading state (already has one — the `#loader` div)

**Estimated effort:** ~30 minutes of coding
**Estimated savings:** ~7.5 MB (from 9 MB to 1.5 MB transferred)
